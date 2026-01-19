# services/dok_bnsp_single.py
import os
from tkinter import messagebox
from config import BASE_DIR, TEMPLATE_BASE, TEMPLATE_DOK_BNSP
from models.peserta_model import PesertaModel
from services.logic import format_kabupaten, format_tanggal_to_general


class DokBNSPSingleProcessor:

    def __init__(self, word_app=None):
        self.word = word_app

    def peserta_to_row(self, tanggal_pelatihan, peserta: PesertaModel, ttd_path, numbering):
        tanggal, bulan, tahun = format_tanggal_to_general(tanggal_pelatihan)

        return {
            'Numbering': str(numbering),
            'Name': peserta.nama,
            'Skema': peserta.skema,
            'ID_Number': peserta.nik,
            'Place_DOB': f"{peserta.tempat_lahir}, {peserta.tanggal_lahir}",
            'Address': (
                f"{peserta.alamat}, KEL. {peserta.kelurahan}, "
                f"KEC. {peserta.kecamatan}, "
                f"{format_kabupaten(peserta.kabupaten)}, {peserta.provinsi}"
            ),
            'Phone_Number': peserta.telepon,
            'Last_Edu': peserta.pendidikan,
            'Date_Participate': f"{tanggal}/{bulan}/{tahun}",
            'Dp_b': f"{tanggal} {bulan} {tahun}",
            'ttd_participant': ttd_path
        }

    def process(self, index, tanggal_pelatihan, peserta: PesertaModel, ttd_path, output_folder, callback_progress):
        """
        Proses single peserta
        """
        templates = TEMPLATE_DOK_BNSP.get(peserta.skema)
        if not templates:
            messagebox.showinfo(
                "Informasi",
                f"Skema '{peserta.skema}' tidak ditemukan"
            )
            return False

        template_paths = [
            os.path.join(BASE_DIR, TEMPLATE_BASE, t.strip())
            for t in templates if t.strip()
        ]

        row_data = self.peserta_to_row(
            tanggal_pelatihan,
            peserta,
            ttd_path,
            index
        )

        for template in template_paths:
            if not self._generate_document(peserta.id_peserta, row_data, template, output_folder, callback_progress):
                return False

        return True

    # === Word generation (dipindah utuh dari class lama) ===
    def _generate_document(self, id_peserta, row_data, template_path, output_folder, callback_progress):
        import time
        import pandas as pd
        import win32com.client as win32
        from colorama import Fore as color, Style

        doc = None
        try:
            os.makedirs(output_folder, exist_ok=True)

            placeholder_mapping = {
                'numbering': 'Numbering',
                'name': 'Name',
                'id_number': 'ID_Number',
                'place_dob': 'Place_DOB',
                'address': 'Address',
                'phone_number': 'Phone_Number',
                'last_edu': 'Last_Edu',
                'date_participate': 'Date_Participate',
                'dp_b': 'Dp_b',
                'ttd_participant': 'ttd_participant'
            }

            wdReplaceAll = 2

            if not self.word:
                self.word = win32.DispatchEx("Word.Application")
                self.word.Visible = False

            doc = self.word.Documents.Open(template_path)
            time.sleep(0.3)
            
            replacements = {}
            for placeholder, column in placeholder_mapping.items():
                if pd.notna(row_data[column]):
                    replacements[placeholder] = str(row_data[column])
                else:
                    replacements[placeholder] = ""

            content = doc.Content

            x = 0
            for placeholder, column in placeholder_mapping.items():
                x += 1
                value = row_data.get(column, '')
                replacement = str(value) if pd.notna(value) else ""

                find = content.Find
                find.ClearFormatting()

                if placeholder == "ttd_participant" and replacement: 
                    try:
                        while True:
                            found = find.Execute(
                                FindText=placeholder,
                                MatchCase=False,
                                MatchWholeWord=False,
                                Forward=True,
                                Wrap=1,
                                Replace=0
                            )
                            if not found:
                                break
                            
                            rng = find.Parent  
                            rng.Text = ""  

                            shape = rng.InlineShapes.AddPicture(
                                FileName=replacement,
                                LinkToFile=False,
                                SaveWithDocument=True
                            )

                            # Box: 4 cm x 2.5 cm
                            if "kpt-c" in template_path and "a" in template_name:
                                max_width = 85.05   # 3 cm
                                max_height = 56.7        
                            else:                
                                max_width = 113.4
                                max_height = 70.9
                            w, h = shape.Width, shape.Height
                            ratio = min(max_width / w, max_height / h)
                            shape.Width = w * ratio
                            shape.Height = h * ratio 
                    except Exception as e:
                        doc.Close(SaveChanges=False)  
                        return False
                else:
                    find.Text = placeholder
                    find.Replacement.ClearFormatting()
                    find.Replacement.Text = replacement
                    find.Execute(
                        FindText=placeholder,
                        MatchCase=False,
                        MatchWholeWord=False,
                        MatchWildcards=False,
                        MatchSoundsLike=False,
                        MatchAllWordForms=False,
                        Forward=True,
                        Wrap=1,  # wdFindContinue
                        Format=False,
                        ReplaceWith=replacement,
                        Replace=wdReplaceAll
                    )
                if x < len(replacements.items()):
                    percent = x / len(replacements.items()) * 100
                    callback_progress(id_peserta, percent)
                    

            template_name = os.path.basename(template_path).split(".")[0]
            kode = "_".join(template_name.replace("dok_", "").split('_')[:-1])

            filename = (
                f"{row_data['Numbering']}-DOK-{kode.upper()} - "
                f"{row_data['Name'].upper()} - "
                f"{row_data['Skema'].upper()}.docx"
            )

            output_path = os.path.join(output_folder, filename)
            doc.SaveAs(output_path)
            return True

        except Exception as e:
            print(color.RED, "Gagal generate:", e, Style.RESET_ALL)
            return False

        finally:
            if doc:
                doc.Close(SaveChanges=False)
                
                
                
# services/dok_bnsp_batch.py
from tkinter import messagebox

class DokBNSPBatchProcessor:

    def __init__(self):
        self.single_processor = DokBNSPSingleProcessor()

    def batch_process(
        self,
        tanggal_pelatihan,
        peserta_list,
        list_ttd_path,
        output_folder,
        progress_callback=None,
        progress_global_callback=None,
        completion_callback=None
    ):
        total = len(peserta_list)

        for index, peserta in enumerate(peserta_list, start=1):
            peserta: PesertaModel
            try:
                result = self.single_processor.process(
                    index,
                    tanggal_pelatihan,
                    peserta,
                    list_ttd_path[peserta.id_peserta],
                    output_folder,
                    progress_callback
                )

                if not result:
                    completion_callback(False)
                    return

                if progress_global_callback:
                    progress_global_callback(index, total)

            except Exception as e:
                messagebox.showinfo(
                    "Informasi",
                    f"Error {peserta.nama}: {str(e)}"
                )
                if completion_callback:
                    completion_callback(False)
                return 
        if completion_callback:
            completion_callback(True)
        return 

    def cleanup(self):
        if self.single_processor.word:
            self.single_processor.word.Quit()
            self.single_processor.word = None

