# =======================
# FILE: services/export_dok_bnsp.py
# =======================
import pandas as pd
import os
# import logging
# from datetime import datetime
import sys
import time
from config import BASE_DIR,TEMPLATE_BASE,TEMPLATE_DOK_BNSP
from tkinter import messagebox
from services.logic import format_kabupaten,format_tanggal_to_general

################# Perbaiki dibagian To Dict ,untuk date partispasi agar pakai teks month nya ,pokoknya sesuaikan format asli

class export_Dok_BNSP:
    
    def __init__(self):
        """Initialize exporter"""
        self.word = None
        self.setup_dependencies()
    
    def setup_dependencies(self):
        """Setup required dependencies"""
        try:
            import win32com.client
        except ImportError:
            # logging.error("The win32com library is not installed. Installing...")
            print("Installing required library (pywin32)...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pywin32"])
            print("Installation complete.")

    def export_dokumen(self, tanggal_pelatihan, peserta_list, ttd_path, output_folder, progress_callback=None):
        """
        Export dokumen dari list peserta
        
        Args:
            peserta_list (list): List of PesertaModel objects
            skema_map (dict): Mapping dari nama skema ke skema_alt
            template_folder (str): Folder template
            output_folder (str): Folder output
            progress_callback (callable): Callback untuk update progress
        """
        total = len(peserta_list)
        successful = 0
        for index, peserta in enumerate(peserta_list, start=1):
            try:
                # Get skema_alt from map
                all_template_name = TEMPLATE_DOK_BNSP.get(peserta.skema)
                if not all_template_name:
                    messagebox.showinfo("Informasi",f"Skema '{peserta.skema}' not found in config.txt, skipping...")
                    continue
                all_template_path = [os.path.join(BASE_DIR,TEMPLATE_BASE, v.strip()) for v in all_template_name if v.strip()]
                # Convert peserta to row format
                row_data = self._peserta_to_row(tanggal_pelatihan, peserta, ttd_path[peserta.id_peserta], index)
                
                # Process
                success = self.process_row(index, row_data, all_template_path, output_folder)
                    
                if success:
                    successful += 1
                
                # Update progress
                if progress_callback:
                    progress_callback(index, total)
                    
            except Exception as e:
                messagebox.showinfo("Informasi",f"Error processing {peserta.nama}: {str(e)}")
                continue
        
        return successful
    
    def _peserta_to_row(self, tanggal_pelatihan, peserta, ttd_path, numbering):
        """Convert PesertaModel to row dict"""
        tanggal, bulan, tahun = format_tanggal_to_general(tanggal_pelatihan)
        return {
            'Numbering': str(numbering),
            'Name': peserta.nama,
            'Skema': peserta.skema,
            'ID_Number': peserta.nik,
            'Place_DOB': f"{peserta.tempat_lahir}, {peserta.tanggal_lahir}",
            'Address': f"{peserta.alamat}, KEL. {peserta.kelurahan}, KEC. {peserta.kecamatan}, {format_kabupaten(peserta.kabupaten)}, {peserta.provinsi}",
            'Phone_Number': peserta.telepon,
            'Last_Edu': peserta.pendidikan,
            'Date_Participate': f"{tanggal}/{bulan}/{tahun}",  
            'Dp_b': f"{tanggal} {bulan} {tahun}",  
            'ttd_participant': ttd_path
        }
    
    def process_row(self, index, row_data, all_template_path, output_folder):
        """
        Process single row and generate documents
        
        Returns:
            bool: True if successful
        """
        
        # # Skema fullname mapping
        # # skema_fullname = {
        #     "apb": "AHLI PENGENDALI BOR",
        #     "apps": "AHLI PENGENDALI PERAWATAN SUMUR",
        #     "forklift": "OPERATOR FORKLIFT",
        #     "kpt-c": "OPERATOR KRAN PUTAR TETAP KELAS-C",
        #     "olb": "OPERATOR LANTAI BOR",
        #     "omps": "OPERATOR MENARA PERAWATAN SUMUR",
        #     "okm-b": "OPERATOR KRAN MOBIL KELAS-B",
        #     "okm-c": "OPERATOR KRAN MOBIL KELAS-C",
        #     "olps": "OPERATOR LANTAI PERAWATAN SUMUR",
        #     "oups": "OPERATOR UNIT PERAWATAN SUMUR",
        #     "tkbt": "K3 BEKERJA DIKETINGGIAN-TKBT2",
        #     "oprt_k3": "OPERATOR K3 MIGAS",
        #     "ahli_k3": "AHLI K3 UMUM",
        #     "peng_k3": "PENGAWAS K3 MIGAS",
        #     "petugas_k3": "PETUGAS K3",
        #     "operator_scaff": "OPERATOR SCAFFOLDING",
        #     "rigger": "JURU IKAT BEBAN",
        #     "crane_insp": "INSPEKTUR PESAWAT ANGKAT",
        #     "juru_bor": "JURU BOR DARAT",
        #     "omb": "OPERATOR MENARA BOR",
        #     "oprt_crane_mbl": "OPERATOR KRAN MOBIL KELAS-A",
        #     "gastester": "OPERATOR GAS TESTER MIGAS",
        #     "welder_6g": "PENGELASAN PIPA - 6G"
        # }
        
        # if skema_alt not in sub_skema:
        #     print(f"{color.RED}Template tidak tersedia untuk: {skema_alt}{Style.RESET_ALL}")
        #     return False
        
        # Process each tipe
        all_success = True
        for template in all_template_path:
            # Find template
            if not os.path.exists(template):
                messagebox.showerror("Error Informasi",f"Template tidak ditemukan: {template}(x)")
                all_success = False
                return
                        
            # Generate document
            success = self.generate_document(
                row_data, 
                index, 
                template, 
                output_folder,
            )
            
            if not success:
                all_success = False
        
        return all_success
    
    def generate_document(self, row_data, index, template_path, output_folder):
        """
        Generate single document from template
        
        Returns:
            bool: True if successful
        """
        from colorama import Fore as color, Style
        import win32com.client as win32
        
        try:
            # Create output folder
            os.makedirs(output_folder, exist_ok=True)
            
            # Placeholder mapping
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
            
            # Word constants
            wdReplaceAll = 2
            # nama_display = f"({row_data['Name'].split()[0]})" if row_data['Name'] else ""
            
            # Progress display
            template_name = os.path.basename(template_path).split(".")[0]
                
            # Start Word
            if not self.word:
                self.word = win32.DispatchEx("Word.Application")
                self.word.Visible = False
            
            # Open template
            doc = self.word.Documents.Open(template_path)
            time.sleep(0.5)
            
            try:
                print("[REPLACE] Start replace placeholders")
                # Prepare replacements
                replacements = {}
                for placeholder, column in placeholder_mapping.items():
                    value = row_data.get(column, '')
                    replacements[placeholder] = str(value) if pd.notna(value) else ""
                
                # Get document content
                content = doc.Content
                
                # Replace placeholders
                progress_steps = len(replacements)
                for step, (placeholder, replacement) in enumerate(replacements.items(), start=1):              
                    find_obj = content.Find
                    find_obj.ClearFormatting()
                    
                    # Special handling for signature image
                    if placeholder == "ttd_participant" and replacement and os.path.exists(replacement):
                        try:
                            while True:
                                found = find_obj.Execute(
                                    FindText=placeholder,
                                    MatchCase=False,
                                    MatchWholeWord=False,
                                    Forward=True,
                                    Wrap=1,
                                    Replace=0
                                )
                                if not found:
                                    break
                                
                                rng = find_obj.Parent
                                rng.Text = ""
                                
                                # Insert image
                                shape = rng.InlineShapes.AddPicture(
                                    FileName=replacement,
                                    LinkToFile=False,
                                    SaveWithDocument=True
                                )
                                
                                # Resize image
                                if "kpt-c" in template_path and "a" in template_name:
                                    max_width = 85.05
                                    max_height = 56.7
                                else:
                                    max_width = 113.4
                                    max_height = 70.9
                                
                                w, h = shape.Width, shape.Height
                                ratio = min(max_width / w, max_height / h)
                                shape.Width = w * ratio
                                shape.Height = h * ratio
                                
                        except Exception as e:
                            print(f'\n{color.RED}Error: TTD image not found or invalid{Style.RESET_ALL}')
                            doc.Close(SaveChanges=False)
                            return False
                    else:
                        # Text replacement
                        find_obj.Text = placeholder
                        find_obj.Replacement.ClearFormatting()
                        find_obj.Replacement.Text = replacement
                        find_obj.Execute(
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
                    
                    # percent = step / progress_steps * 100
                    # bar = f"{'#' * (step * 2)}{'-' * ((progress_steps - step) * 2)}"
                    # if tipe == "a":
                    #     print(f'{index}.{nama_display.ljust(15)} {template_name.ljust(30)} [{bar}] {percent:5.0f}%', end='\r', flush=True)
                    # else:
                    #     prefix = "   " if index >= 10 else "  "
                    #     print(f'{prefix}{nama_display.ljust(15)} {template_name.ljust(30)} [{bar}] {percent:5.0f}%', end='\r', flush=True)
            except Exception as e:
                print("[REPLACE] Error saat replace")
                print(e)
                raise
            
            try:
                # Save document
                kode = "_".join(os.path.splitext(template_name)[0].replace("dok_", "", 1).split('_')[:-1])
                filename = f"{row_data['Numbering']}-DOK-{kode.upper()} - {row_data['Name'].upper()} - {row_data['Skema'].upper()}{os.path.splitext(os.path.basename(template_path))[1]}"
                sanitized_filename = "".join(c for c in filename if c.isalnum() or c in " ._-")
                output_path = os.path.abspath(os.path.join(output_folder, sanitized_filename))
                try:
                    doc.SaveAs2(output_path)
                except AttributeError:
                    doc.SaveAs(output_path)
            except Exception as e:
                print("[SAVE] Error saat save")
                print(e)
                raise
                
            time.sleep(0.5)
            return True
            
        except Exception as e:
            print("[DOC] Gagal generate dokumen")
            print(e)
            return False
        finally:
            if doc:
                try:
                    doc.Close(SaveChanges=False)
                    print("[CLOSE] Document closed")
                except Exception as e:
                    print("[CLOSE] Gagal close document")
                    print(e)
    
    def cleanup(self):
        """Cleanup Word instance"""
        try:
            if self.word:
                self.word.Quit()
                self.word = None
                # logging.info("Word application closed")
        except:
            pass
    
    def __del__(self):
        """Destructor"""
        self.cleanup()