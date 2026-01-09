# =======================
# FILE: pages/import_dialog.py
# =======================
import customtkinter as ctk
from tkinter import messagebox
import uuid
from datetime import datetime
from pages.peserta_model import PesertaModel
from services.database import DB_Save_Peserta_Batch, DB_Save_Sertifikasi

class ImportDialog(ctk.CTkToplevel):
    def __init__(self, parent, callback, id_sertifikasi=None):
        super().__init__(parent)
        
        self.id_sertifikasi = id_sertifikasi
        self.callback = callback
        self.parsed_data = []
        
        # Window setup
        self.title("📥 Import Data dari Excel")
        self.geometry("1000x500")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Center window
        self.center_window()
        
        self.create_widgets()
        
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
   
    def create_widgets(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="#1a73e8", height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="📥 Import Data Peserta",
            font=("Arial", 22, "bold"),
            text_color="white"
        ).pack(pady=20)
        
        # 🔥 COMBO BOX FRAME - DI BAWAH INSTRUCTIONS, DI ATAS CONTAINER
        combo_frame = ctk.CTkFrame(self, fg_color="#1f1f1f")
        combo_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Sertifikasi Selection
        sertif_container = ctk.CTkFrame(combo_frame, fg_color="transparent")
        sertif_container.pack(side="left", padx=15, pady=10)
        
        ctk.CTkLabel(
            sertif_container,
            text="Sertifikasi:",
            font=("Arial", 13, "bold")
        ).pack(side="left", padx=(0, 8))
        
        # Load sertifikasi options
        from services.database import DB_Get_All_Sertifikasi
        self.all_sertifikasi = DB_Get_All_Sertifikasi()
        sertif_options = self._generate_sertifikasi_options()
        
        self.sertif_combo = ctk.CTkComboBox(
            sertif_container,
            values=sertif_options,
            width=250,
            height=35,
            state="readonly"
        )
        self.sertif_combo.pack(side="left")
        
        # Set default value berdasarkan parameter
        if self.id_sertifikasi and sertif_options:
            self._set_sertifikasi_by_id(self.id_sertifikasi)
        elif sertif_options:
            self.sertif_combo.set(sertif_options[0])
            self._update_selected_id()
        
        # Format Selection
        format_container = ctk.CTkFrame(combo_frame, fg_color="transparent")
        format_container.pack(side="left", padx=15, pady=10)
        
        ctk.CTkLabel(
            format_container,
            text="Format Import:",
            font=("Arial", 13, "bold")
        ).pack(side="left", padx=(0, 8))
        
        self.format_combo = ctk.CTkComboBox(
            format_container,
            values=["AWL-Copy", "Rekap BNSP", "AWL Report"],
            width=180,
            height=35,
            state="readonly"
        )
        self.format_combo.set("AWL-Copy")
        self.format_combo.pack(side="left")
        
        # Textarea untuk paste
        text_frame = ctk.CTkFrame(self, fg_color="transparent")
        text_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        ctk.CTkLabel(
            text_frame,
            text="Paste Data di sini:",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.text_area = ctk.CTkTextbox(
            text_frame,
            font=("Courier New", 11),
            wrap="none"
        )
        self.text_area.pack(fill="both", expand=True)
        
        # Preview area (hidden initially)
        self.preview_frame = ctk.CTkFrame(self, fg_color="#1f1f1f")
        self.preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="",
            font=("Arial", 13),
            text_color="#4caf50"
        )
        self.preview_label.pack(pady=10)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkButton(
            btn_frame,
            text="❌ Batal",
            width=120,
            height=40,
            fg_color="#666666",
            hover_color="#555555",
            command=self.destroy
        ).pack(side="left")
        
        ctk.CTkButton(
            btn_frame,
            text="🔄 Parse Data",
            width=150,
            height=40,
            fg_color="#ff9800",
            hover_color="#f57c00",
            command=self.parse_data
        ).pack(side="left", padx=10)
        
        self.save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Simpan ke Database",
            width=180,
            height=40,
            fg_color="#4caf50",
            hover_color="#45a049",
            command=self.save_to_database,
            state="disabled"
        )
        self.save_btn.pack(side="right")
  
    def _generate_sertifikasi_options(self):
        """Generate options untuk combo box sertifikasi"""
        options = []
        self.sertifikasi_map = {}
        
        for sert in self.all_sertifikasi:
            # Truncate nama jika terlalu panjang
            nama = sert["sertifikasi"]
            if len(nama) > 30:
                nama = nama[:27] + "..."
            
            tanggal = sert["tanggal_pelatihan"]
            display_text = f"{nama} - {tanggal}"
            
            # Simpan mapping
            self.sertifikasi_map[display_text] = sert["id_sertifikasi"]
            options.append(display_text)
        
        return options

    def _set_sertifikasi_by_id(self, id_sertifikasi):
        """Set combo box berdasarkan ID yang dikirim"""
        for display_text, sert_id in self.sertifikasi_map.items():
            if sert_id == id_sertifikasi:
                self.sertif_combo.set(display_text)
                self.id_sertifikasi = id_sertifikasi
                return

    def _update_selected_id(self):
        """Update id_sertifikasi berdasarkan combo box"""
        current_text = self.sertif_combo.get()
        self.id_sertifikasi = self.sertifikasi_map.get(current_text, "")
   
    def parse_data(self):
        """Parse data based on selected format"""
        format_type = self.format_combo.get()
        
        if format_type == "AWL-Copy":
            self.parse_awl_copy()
        elif format_type == "Rekap BNSP":
            self.parse_rekap_bnsp()
        elif format_type == "AWL Report":
            self.parse_awl_report()
        else:
            messagebox.showerror("Error", "Format tidak dikenali!")
    
    def parse_awl_copy(self):
        """Parse AWL-Copy format"""
        raw_text = self.text_area.get("1.0", "end-1c").strip()
        
        if not raw_text:
            messagebox.showwarning("Peringatan", "Area teks kosong! Paste data terlebih dahulu.")
            return
        
        try:
            lines = raw_text.split('\n')
            
            if len(lines) < 2:
                messagebox.showerror("Error", "Format data tidak valid! Minimal harus ada header dan 1 peserta.")
                return
            
            # Parse header (line pertama)
            header_line = lines[0]
            header_data = self.extract_fields(header_line)
            
            if len(header_data) < 3:
                messagebox.showerror("Error", "Header tidak valid! Format: ⟦AWL-Copy⟧⟦Nama Sertifikasi⟧⟦Tanggal⟧")
                return
            
            format_marker = header_data[0]
            if format_marker != "AWL-Copy":
                messagebox.showerror("Error", "Bukan format AWL-Copy yang valid!")
                return
            
            nama_sertifikasi = header_data[1]
            tanggal_pelatihan = header_data[2]
            
            # Parse peserta (baris selanjutnya)
            self.parsed_data = []
            errors = []
            
            for i, line in enumerate(lines[1:], start=1):
                if not line.strip():
                    continue
                
                try:
                    fields = self.extract_fields(line)
                    
                    if len(fields) < 14:
                        errors.append(f"Baris {i}: Kurang field (hanya {len(fields)})")
                        continue
                    
                    peserta = PesertaModel(
                        id_peserta=str(uuid.uuid4()),
                        id_sertifikasi="",  # Will be filled when saving
                        skema=fields[2],
                        nama=fields[1],
                        nik=fields[3],
                        tempat_lahir=fields[4],
                        tanggal_lahir=fields[5],
                        alamat=fields[6],
                        kelurahan=fields[7],
                        kecamatan=fields[8],
                        kabupaten=fields[9],
                        provinsi=fields[10],
                        telepon=fields[11],
                        pendidikan=fields[12],
                        instansi=fields[13]
                    )
                    
                    self.parsed_data.append({
                        'peserta': peserta,
                        'tanggal_pelatihan': tanggal_pelatihan,
                        'nama_sertifikasi': nama_sertifikasi
                    })
                    
                except Exception as e:
                    errors.append(f"Baris {i}: Error parsing - {str(e)}")
            
            # Show results
            if errors:
                error_msg = "\n".join(errors[:5])
                if len(errors) > 5:
                    error_msg += f"\n... dan {len(errors)-5} error lainnya"
                messagebox.showwarning(
                    "Peringatan Parsing",
                    f"❌ {len(errors)} baris gagal diparse:\n\n{error_msg}"
                )
            
            if self.parsed_data:
                self.preview_frame.pack(fill="x", padx=20, pady=(0, 10))
                self.preview_label.configure(
                    text=f"✅ Berhasil parse {len(self.parsed_data)} peserta | "
                         f"❌ {len(errors)} error\n"
                         f"📜 Sertifikasi: {nama_sertifikasi} | 📅 Tanggal: {tanggal_pelatihan}"
                )
                self.save_btn.configure(state="normal")
                messagebox.showinfo(
                    "Sukses",
                    f"✅ Berhasil parse {len(self.parsed_data)} peserta!\n\n"
                    f"Sertifikasi: {nama_sertifikasi}\n"
                    f"Tanggal: {tanggal_pelatihan}\n\n"
                    f"Silakan klik 'Simpan ke Database' untuk menyimpan."
                )
            else:
                messagebox.showerror("Error", "Tidak ada data yang berhasil diparse!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Gagal parsing data:\n{str(e)}")
    
    def extract_fields(self, line):
        """Extract fields from AWL-Copy format: ⟦field1⟧⟦field2⟧..."""
        fields = []
        current_field = ""
        in_bracket = False
        
        i = 0
        while i < len(line):
            if i < len(line) - 1 and line[i:i+1] == '⟦':
                in_bracket = True
                i += 1
                continue
            elif i < len(line) - 1 and line[i:i+1] == '⟧':
                in_bracket = False
                fields.append(current_field)
                current_field = ""
                i += 1
                continue
            
            if in_bracket:
                current_field += line[i]
            
            i += 1
        
        return fields
    
    def parse_rekap_bnsp(self):
        """Parse Rekap BNSP format - Placeholder"""
        messagebox.showinfo(
            "Info",
            "Format Rekap BNSP belum diimplementasikan.\n"
            "Akan segera ditambahkan."
        )
    
    def parse_awl_report(self):
        """Parse AWL Report format - Placeholder"""
        messagebox.showinfo(
            "Info",
            "Format AWL Report belum diimplementasikan.\n"
            "Akan segera ditambahkan."
        )
    
    def parse_alamat(self, alamat_full: str):
        """
        Parse alamat format:
        JL. PIPA AIR BERSIH..., KEL. SIMPANG PADANG, KEC. BATHIN SOLAPAN
        
        Returns dict dengan keys: alamat, kelurahan, kecamatan
        """
        try:
            parts = [p.strip() for p in alamat_full.split(',')]
            
            result = {
                'alamat': '',
                'kelurahan': '',
                'kecamatan': '',
            }
            
            for part in parts:
                part_upper = part.upper()
                
                if 'KEL.' in part_upper:
                    result['kelurahan'] = part.split('KEL.')[-1].strip()
                elif 'KEC.' in part_upper:
                    result['kecamatan'] = part.split('KEC.')[-1].strip()
                elif not result['alamat']:
                    result['alamat'] = part
            
            return result
            
        except Exception as e:
            return {
                'alamat': alamat_full,
                'kelurahan': '',
                'kecamatan': '',
            }
    
    def save_to_database(self):
        """Simpan semua data ke database"""
        if not self.parsed_data:
            messagebox.showwarning("Peringatan", "Tidak ada data untuk disimpan!")
            return
        
        # Update selected ID dari combo box
        self._update_selected_id()
        
        if not self.id_sertifikasi:
            messagebox.showerror("Error", "Sertifikasi tidak dipilih!")
            return
        
        try:
            total_saved = 0
            
            # Update id_sertifikasi untuk semua peserta
            for item in self.parsed_data:
                item['peserta'].id_sertifikasi = self.id_sertifikasi
            
            # Ambil list peserta saja
            peserta_list = [item['peserta'] for item in self.parsed_data]
            
            # Batch save peserta
            saved = DB_Save_Peserta_Batch(peserta_list, self.id_sertifikasi)
            total_saved += saved
            
            messagebox.showinfo(
                "Sukses",
                f"✅ Berhasil menyimpan:\n\n"
                f"👥 {total_saved} Peserta ke sertifikasi terpilih"
            )
            
            # Callback and close
            if self.callback:
                self.callback()
            
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan data:\n{str(e)}")