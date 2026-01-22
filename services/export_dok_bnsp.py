import os, logging
from config import DEBUG, BASE_DIR, TEMPLATE_BASE, TEMPLATE_DOK_BNSP
from models.peserta_model import PesertaModel
from services.logic import format_kabupaten, format_tanggal_to_general


class DokBNSPSingleProcessor:

    def __init__(self, word_app=None):
        self.word = word_app

    def peserta_to_row(self, numbering, peserta: PesertaModel, tanggal_pelatihan,  ttd_path):
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

    def process(
        self, 
        index, 
        tanggal_pelatihan, 
        peserta: PesertaModel, 
        ttd_path, 
        output_folder, 
        callback_single):
        
        templates = TEMPLATE_DOK_BNSP.get(peserta.skema)
        if not templates:
            if callback_single:
                callback_single(peserta.id_peserta, "error", None)
            if DEBUG:
                logging.warning(f"Template Tidak Tersedia! -> {peserta.skema}")
            return False

        template_paths = [
            os.path.join(BASE_DIR, TEMPLATE_BASE, t.strip())
            for t in templates if t.strip()
        ]

        row_data = self.peserta_to_row(
            index,
            peserta,
            tanggal_pelatihan,
            ttd_path
        )
        
        total_templates = len(template_paths)

        for template_idx, template in enumerate(template_paths, start=1):
            def adjusted_progress_callback(peserta_id, item_progress):
                completed_templates = template_idx - 1
                base_progress = (completed_templates / total_templates) * 100
                
                current_template_progress = (item_progress / 100) * (100 / total_templates)
                
                total_progress = base_progress + current_template_progress
                
                if callback_single:
                    callback_single(peserta_id, "running", total_progress)
                    
            if not self._generate_document(
                peserta.id_peserta, 
                row_data, 
                template, 
                output_folder, 
                adjusted_progress_callback):
                if callback_single:
                    callback_single(peserta.id_peserta, "error", None)
                if DEBUG:
                    logging.error("Generated Dokument Gagal")
                return False
            
        if callback_single:
            callback_single(peserta.id_peserta, "completed", None)
        return True

    def _generate_document(self, id_peserta, row_data, template_path, output_folder, callback_progress):
        import pandas as pd
        import win32com.client as win32

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
            
            replacements = {}
            for placeholder, column in placeholder_mapping.items():
                if pd.notna(row_data[column]):
                    replacements[placeholder] = str(row_data[column])
                else:
                    replacements[placeholder] = ""

            content = doc.Content

            total_items = len(replacements)
            basename = os.path.basename(template_path)
            template_name, ext = os.path.splitext(basename)
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
                        if DEBUG:
                            logging.error(f"[Error] TTD Replacement Area -> {e}")
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
                        Wrap=1,  
                        Format=False,
                        ReplaceWith=replacement,
                        Replace=wdReplaceAll
                    )
                if callback_progress:
                    item_progress = (x / total_items) * 100
                    callback_progress(id_peserta, item_progress)
                                
            kode = "_".join(template_name.replace("dok_", "").split('_')[:-1])

            filename = (
                f"{row_data['Numbering']}-DOK-{kode.upper()} - "
                f"{row_data['Name'].upper()} - "
                f"{row_data['Skema'].upper()}{ext}"
            )

            output_path = os.path.join(output_folder, filename)
            doc.SaveAs(output_path)
            return True

        except Exception as e:
            if DEBUG:
                logging.error(f"Gagal generate dokumen -> {e}")
            return False

        finally:
            if doc:
                doc.Close(SaveChanges=False)
                
    def cleanup(self):
        if self.current_doc:
            try:
                self.current_doc.Close(SaveChanges=False)
            except:
                pass
            self.current_doc = None
        
        if self.word:
            try:
                self.word.Quit()
            except:
                pass
            self.word = None              
                
class DokBNSPBatchProcessor:

    def __init__(self):
        self.single_processor = DokBNSPSingleProcessor()

    def batch_process(
        self,
        tanggal_pelatihan,
        peserta_list,
        list_ttd_path,
        output_folder,
        callback_single,
        callback_global
    ):
        for index, peserta in enumerate(peserta_list, start=1):
            peserta: PesertaModel
            try:
                result = self.single_processor.process(
                    index,
                    tanggal_pelatihan,
                    peserta,
                    list_ttd_path[peserta.id_peserta],
                    output_folder,
                    callback_single,
                )

                if not result:
                    if callback_global:
                        callback_global('error')
                    return

            except Exception as e:
                if DEBUG:
                    logging.error(f"[Error] Batch Processor -> {e}")
                return 
            
        if callback_global:
            callback_global('completed')
        return 
            
    def cleanup(self):
        if self.single_processor.word:
            self.single_processor.word.Quit()
            self.single_processor.word = None

