# =======================
# FILE: pages/export_dialog.py
# =======================
import customtkinter as ctk
from tkinter import messagebox, filedialog
from services.export_rekap_bnsp import export_Rekap_BNSP
from services.export_dok_bnsp import export_Dok_BNSP
from config import NAMA_PERUSAHAAN,EMAIL,LOKASI_PERUSAHAAN
from services.logic import return_format_tanggal,get_text_hari
import os
from datetime import datetime
from pages.peserta_model import PesertaModel

class ExportDialog(ctk.CTkToplevel):
    def __init__(self, parent, peserta_list, sertifikasi_info, callback):
        super().__init__(parent)
        
        self.callback = callback
        self.peserta_list = peserta_list
        self.sertifikasi_info = sertifikasi_info
        self.last_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.selected_files = {}  # Store selected files per peserta
        
        # Window setup
        self.title("📤 Ekspor Data Peserta")
        self.geometry("900x600")
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
            text="📤 Ekspor Data Peserta",
            font=("Arial", 22, "bold"),
            text_color="white"
        ).pack(pady=20)
        
        # Format Selection
        format_frame = ctk.CTkFrame(self, fg_color="#1f1f1f")
        format_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            format_frame,
            text="Pilih Format Ekspor:",
            font=("Arial", 14, "bold")
        ).pack(side="left", padx=15, pady=10)
        
        self.format_combo = ctk.CTkComboBox(
            format_frame,
            values=["Rekap BNSP", "AWL Report", "Dokumen BNSP"],
            width=200,
            height=35,
            state="readonly",
            command=self.on_format_changed
        )
        self.format_combo.set("Rekap BNSP")
        self.format_combo.pack(side="left", padx=10, pady=10)
        
        # Content container (scrollable)
        self.content_container = ctk.CTkScrollableFrame(
            self,
            fg_color="#2a2a2a"
        )
        self.content_container.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Bottom buttons
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
            text="📤 Ekspor",
            width=150,
            height=40,
            fg_color="#4caf50",
            hover_color="#45a049",
            command=self.do_export
        ).pack(side="right")
        
        # Load initial format
        self.on_format_changed("Rekap BNSP")
    
    def on_format_changed(self, selected_format):
        """Handle format change"""
        # Clear container
        for widget in self.content_container.winfo_children():
            widget.destroy()
        
        if selected_format == "Rekap BNSP":
            self.render_rekap_bnsp()
        elif selected_format == "AWL Report":
            self.render_awl_report()
        elif selected_format == "Dokumen BNSP":
            self.render_dokumen_bnsp()
    
    def render_rekap_bnsp(self):
        """Render format Rekap BNSP"""
        # Header
        header_frame = ctk.CTkFrame(self.content_container, fg_color="#333333", height=40)
        header_frame.pack(fill="x", pady=(0, 5))
        header_frame.pack_propagate(False)
        
        header_frame.grid_columnconfigure(0, weight=0, minsize=50)
        header_frame.grid_columnconfigure(1, weight=1, minsize=300)
        header_frame.grid_columnconfigure(2, weight=0, minsize=150)
        
        ctk.CTkLabel(header_frame, text="No", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, sticky="w")
        ctk.CTkLabel(header_frame, text="Nama Peserta", font=("Arial", 12, "bold")).grid(row=0, column=1, padx=10, sticky="w")
        ctk.CTkLabel(header_frame, text="Jenis Kelamin", font=("Arial", 12, "bold")).grid(row=0, column=2, padx=10, sticky="w")
        
        # Rows
        for i, peserta in enumerate(self.peserta_list, start=1):
            row_frame = ctk.CTkFrame(self.content_container, fg_color="#2a2a2a")
            row_frame.pack(fill="x", pady=2)
            
            row_frame.grid_columnconfigure(0, weight=0, minsize=50)
            row_frame.grid_columnconfigure(1, weight=1, minsize=300)
            row_frame.grid_columnconfigure(2, weight=0, minsize=150)
            
            ctk.CTkLabel(row_frame, text=str(i), font=("Arial", 11)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(row_frame, text=peserta.nama, font=("Arial", 11)).grid(row=0, column=1, padx=10, pady=5, sticky="w")
            
            gender_combo = ctk.CTkComboBox(
                row_frame,
                values=["Laki-laki", "Perempuan"],
                width=130,
                height=30,
                state="readonly"
            )
            gender_combo.set("Laki-laki")
            gender_combo.grid(row=0, column=2, padx=10, pady=5)
            
            # Store reference
            peserta._gender_widget = gender_combo
    
    def render_awl_report(self):
        """Render format AWL Report"""
        # Header
        header_frame = ctk.CTkFrame(self.content_container, fg_color="#333333", height=40)
        header_frame.pack(fill="x", pady=(0, 5))
        header_frame.pack_propagate(False)
        
        header_frame.grid_columnconfigure(0, weight=0, minsize=80)
        header_frame.grid_columnconfigure(1, weight=1, minsize=400)
        
        ctk.CTkLabel(header_frame, text="No", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, sticky="w")
        ctk.CTkLabel(header_frame, text="Nama Peserta", font=("Arial", 12, "bold")).grid(row=0, column=1, padx=10, sticky="w")
        
        # Rows
        for i, peserta in enumerate(self.peserta_list, start=1):
            row_frame = ctk.CTkFrame(self.content_container, fg_color="#2a2a2a")
            row_frame.pack(fill="x", pady=2)
            
            row_frame.grid_columnconfigure(0, weight=0, minsize=80)
            row_frame.grid_columnconfigure(1, weight=1, minsize=400)
            
            ctk.CTkLabel(row_frame, text=str(i), font=("Arial", 11)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(row_frame, text=peserta.nama, font=("Arial", 11)).grid(row=0, column=1, padx=10, pady=5, sticky="w")
    
    def render_dokumen_bnsp(self):
        """Render format Dokumen BNSP"""
        # Header
        header_frame = ctk.CTkFrame(self.content_container, fg_color="#333333", height=40)
        header_frame.pack(fill="x", pady=(0, 5))
        header_frame.pack_propagate(False)
        
        header_frame.grid_columnconfigure(0, weight=0, minsize=50)
        header_frame.grid_columnconfigure(1, weight=1, minsize=200)
        header_frame.grid_columnconfigure(2, weight=0, minsize=120)
        header_frame.grid_columnconfigure(3, weight=1, minsize=300)
        
        ctk.CTkLabel(header_frame, text="No", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, sticky="w")
        ctk.CTkLabel(header_frame, text="Nama", font=("Arial", 12, "bold")).grid(row=0, column=1, padx=10, sticky="w")
        ctk.CTkLabel(header_frame, text="Jenis Kelamin", font=("Arial", 12, "bold")).grid(row=0, column=2, padx=10, sticky="w")
        ctk.CTkLabel(header_frame, text="File TTD", font=("Arial", 12, "bold")).grid(row=0, column=3, padx=10, sticky="w")
        
        # Rows
        for i, peserta in enumerate(self.peserta_list, start=1):
            row_frame = ctk.CTkFrame(self.content_container, fg_color="#2a2a2a")
            row_frame.pack(fill="x", pady=2)
            
            row_frame.grid_columnconfigure(0, weight=0, minsize=50)
            row_frame.grid_columnconfigure(1, weight=1, minsize=200)
            row_frame.grid_columnconfigure(2, weight=0, minsize=120)
            row_frame.grid_columnconfigure(3, weight=1, minsize=300)
            
            ctk.CTkLabel(row_frame, text=str(i), font=("Arial", 11)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(row_frame, text=peserta.nama, font=("Arial", 11)).grid(row=0, column=1, padx=10, pady=5, sticky="w")
            
            gender_combo = ctk.CTkComboBox(
                row_frame,
                values=["Laki-laki", "Perempuan"],
                width=110,
                height=30,
                state="readonly"
            )
            gender_combo.set("Laki-laki")
            gender_combo.grid(row=0, column=2, padx=10, pady=5)
            
            # File selector container
            file_container = ctk.CTkFrame(row_frame, fg_color="transparent")
            file_container.grid(row=0, column=3, padx=10, pady=5, sticky="ew")
            
            # Path label (scrollable)
            path_label = ctk.CTkLabel(
                file_container,
                text="Belum dipilih",
                font=("Arial", 10),
                text_color="#999999",
                anchor="w"
            )
            path_label.pack(side="left", fill="x", expand=True, padx=(0, 5))
            
            # Browse button
            browse_btn = ctk.CTkButton(
                file_container,
                text="📁 TTD",
                width=70,
                height=30,
                fg_color="#1a73e8",
                hover_color="#1557b0",
                command=lambda p=peserta, lbl=path_label: self.browse_file(p, lbl)
            )
            browse_btn.pack(side="right")
            
            # Store references
            peserta._gender_widget = gender_combo
            peserta._path_label = path_label
    
    def browse_file(self, peserta, path_label):
        """Open file chooser for TTD file"""
        file_path = filedialog.askopenfilename(
            title="Pilih File TTD",
            initialdir=self.last_path,
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            # Update last path
            self.last_path = os.path.dirname(file_path)
            
            # Store file path
            self.selected_files[peserta.id_peserta] = file_path
            
            # Update label
            filename = os.path.basename(file_path)
            path_label.configure(text=filename, text_color="#4caf50")
    
    def do_export(self):
        """Execute export based on selected format"""
        selected_format = self.format_combo.get()
        
        try:
            if selected_format == "Rekap BNSP":
                self.export_rekap_bnsp()
            elif selected_format == "AWL Report":
                self.export_awl_report()
            elif selected_format == "Dokumen BNSP":
                self.export_dokumen_bnsp()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal ekspor:\n{str(e)}")
    
    def export_rekap_bnsp(self):
        """Export Rekap BNSP format"""
        # Collect data with gender
       
        tanggal_pelatihan = return_format_tanggal(self.sertifikasi_info["tanggal_pelatihan"])
        data_peserta = []
        for i, peserta in enumerate(self.peserta_list, start=1):
            gender = peserta._gender_widget.get()
            data_peserta.append({
                'no': i,
                'tuk': NAMA_PERUSAHAAN,
                'tempat': LOKASI_PERUSAHAAN,
                'hari': get_text_hari(),
                'tanggal': tanggal_pelatihan.replace("-","/"), 
                'nama_peserta': peserta.nama,
                'skema': peserta.skema,
                'nik': peserta.nik,
                'tempat_lahir': peserta.tempat_lahir,
                'tanggal_lahir': peserta.tanggal_lahir.replace("-","/"),
                'jenis_kelamin': gender,
                'alamat': f"{peserta.alamat}, KEL. {peserta.kelurahan}, KEC. {peserta.kecamatan}",
                'kabupaten': peserta.kabupaten,
                'provinsi': peserta.provinsi,
                'no_hp': peserta.telepon,
                'email': EMAIL,
                'pendidikan': peserta.pendidikan,
                'pekerjaan': "Kary. Swasta",
                'instansi': peserta.instansi
            })
        
        DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
        TEMPLATE_PATH = "template_rekap_bnsp.xlsx"
        OUTPUT_PATH = os.path.join(DOWNLOAD_DIR, f"[{tanggal_pelatihan}] Rekap Peserta LSP Energi.xlsx")
        
    
        # Export data
        exporter = export_Rekap_BNSP(TEMPLATE_PATH)
        success = exporter.export(data_peserta, OUTPUT_PATH)
        
        if success:
            messagebox.showinfo(
                "E✅ Export berhasil!\n",
                f"File disimpan di: {OUTPUT_PATH}"
            )
        else:
            messagebox.showinfo(
                "E❌ Export gagal!\n"                
            )
        
        if self.callback:
            self.callback()
        self.destroy()
    
    def export_awl_report(self):
        """Export AWL Report format"""
        data = []
        for i, peserta in enumerate(self.peserta_list, start=1):
            data.append({
                'no': i,
                'nama': peserta.nama
            })
        
        # TODO: Implement actual export logic
        messagebox.showinfo(
            "Ekspor AWL Report",
            f"✅ Format: AWL Report\n"
            f"📊 Total: {len(data)} peserta\n\n"
            f"Ekspor akan diimplementasikan..."
        )
        
        if self.callback:
            self.callback()
        self.destroy()
    
    def export_dokumen_bnsp(self):
        """Export Dokumen BNSP format (placeholder)"""
        # Check if all files selected
        missing_files = []
        for peserta in self.peserta_list:
            if peserta.id_peserta not in self.selected_files:
                missing_files.append(peserta.nama)
        
        if missing_files:
            messagebox.showwarning(
                "File Belum Lengkap",
                f"⚠️ File TTD belum dipilih untuk:\n\n" +
                "\n".join(missing_files[:5]) +
                (f"\n... dan {len(missing_files)-5} lainnya" if len(missing_files) > 5 else "")
            )
            return
       
        tanggal_pelatihan = return_format_tanggal(self.sertifikasi_info["tanggal_pelatihan"])
        
        DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
        TEMPLATE_PATH = "template_rekap_bnsp.xlsx"
        OUTPUT_PATH = os.path.join(DOWNLOAD_DIR, f"[{tanggal_pelatihan}] Rekap Peserta LSP Energi.xlsx")
        
    
        # Export data
        exporter = export_Dok_BNSP(TEMPLATE_PATH)
        success, total = exporter.export_dokumen(tanggal_pelatihan, OUTPUT_PATH)
        
        if success:
            messagebox.showinfo(
                "E✅ Export berhasil!\n",
                f"File disimpan di: {OUTPUT_PATH}"
            )
        else:
            messagebox.showinfo(
                "E❌ Export gagal!\n"                
            )
        
        if self.callback:
            self.callback()
        self.destroy()