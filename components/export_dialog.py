# =======================
# FILE: pages/export_dialog.py
# =======================
import customtkinter as ctk
from tkinter import messagebox, filedialog
from models.peserta_model import PesertaModel
from services.export_excel import export_Excel
from services.export_dok_bnsp import DokBNSPSingleProcessor, DokBNSPBatchProcessor
from config import BASE_DIR,NAMA_PERUSAHAAN,EMAIL,LOKASI_PERUSAHAAN,TEMPLATE_AWL_REPORT,TEMPLATE_REKAP_BNSP
from services.logic import return_format_tanggal,get_text_hari,format_kabupaten
import os, threading, queue, logging

class ExportDialog(ctk.CTkToplevel):
    def __init__(self, parent, peserta_list, sertifikasi_info, callback):
        super().__init__(parent)
        
        self.callback = callback
        self.peserta_list = peserta_list
        self.sertifikasi_info = sertifikasi_info
        self.last_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.selected_files = {}  # Store selected files per peserta
        
        self.progress_value = 0
        self.progress_label_text = ""
        self.is_exporting = False
        
        self.individual_processors = {}  
        self.peserta_rows = {} 
        self.progress_queue = queue.Queue()

        # Window setup
        self.title("📤 Ekspor Data Peserta")
        self.geometry("900x550")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Center window
        self.center_window()
        
        self.create_widgets()
        # self._process_queue()
        
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2) + 50
        y = (self.winfo_screenheight() // 2) - (height // 2) - 20
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
        btn_frame = ctk.CTkFrame(self, fg_color="#2a2a2a", height=60)
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        btn_frame.pack_propagate(False)


        # Center: Progress bar container (initially hidden)
        self.status_container = ctk.CTkFrame(btn_frame, fg_color="transparent", height=120)
        self.status_container.pack(side="left", fill="x", expand=True, padx=20)
        self.status_container.pack_propagate(False)  # PENTING: maintain height
        # Progress frame (shown during export)
        self.progress_frame = ctk.CTkFrame(self.status_container, fg_color="#2a2a2a", corner_radius=10)

        # Progress percentage label
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="0%",
            font=("Arial", 13, "bold"),
            text_color="#999999"
        )
        self.progress_label.pack(pady=(10, 2))

        # Progress bar with modern styling
        self.global_progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            width=300,
            height=10,
            corner_radius=5,
            fg_color="#333333",
            progress_color="#4caf50"
        )
        self.global_progress_bar.pack(pady=(0, 10), padx=15)
        self.global_progress_bar.set(0)

        # Success message frame (shown after completion)
        self.success_frame = ctk.CTkFrame(self.status_container, fg_color="#1f1f1f", corner_radius=10)

        self.success_icon = ctk.CTkLabel(
            self.success_frame,
            text="✅",
            font=("Arial", 24)
        )
        self.success_icon.pack(pady=(10, 5))

        self.success_label = ctk.CTkLabel(
            self.success_frame,
            text="Export berhasil!",
            font=("Arial", 13, "bold"),
            text_color="#4caf50"
        )
        self.success_label.pack(pady=0)

        self.success_path = ctk.CTkLabel(
            self.success_frame,
            text="",
            font=("Arial", 10),
            text_color="#999999",
            wraplength=350
        )
        self.success_path.pack(pady=(2, 10), padx=15)

        # Export button (will be hidden during export)
        self.export_btn = ctk.CTkButton(
            btn_frame,
            text="📤 Ekspor",
            width=150,
            height=40,
            fg_color="#4caf50",
            hover_color="#45a049",
            command=self.do_export
        )
        self.export_btn.pack(side="right", padx=20)
        
        # Load initial format
        self.on_format_changed("Rekap BNSP")
    
    # def _process_queue(self):
    #     """Process updates from worker threads"""
    #     try:
    #         while True:
    #             try:
    #                 update = self.progress_queue.get_nowait()
                    
    #                 # Execute update based on type
    #                 if update['type'] == 'row_progress':
    #                     self._on_row_progress(
    #                         update['peserta_id'],
    #                         update['progress']
    #                     )
    #                 elif update['type'] == 'row_completed':
    #                     self._on_row_completed(update['peserta_id'])
    #                 elif update['type'] == 'row_error':
    #                     self._on_row_error(update['peserta_id'], update['message'])
    #                 elif update['type'] == 'global_progress':
    #                     self.update_progress(update['value'])
                    
    #             except queue.Empty:
    #                 break
    #     except:
    #         pass
        
    #     # Schedule next check (every 50ms)
    #     self.after(50, self._process_queue)
        
    def on_format_changed(self, selected_format):
        """Handle format change"""
        self.reset_ui_state()
        
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
        """Render format Dokumen BNSP dengan individual run button"""
        # Header
        header_frame = ctk.CTkFrame(self.content_container, fg_color="#333333", height=40)
        header_frame.pack(fill="x", pady=(0, 5))
        header_frame.pack_propagate(False)
        
        header_frame.grid_columnconfigure(0, weight=0, minsize=50)   # No
        header_frame.grid_columnconfigure(1, weight=1, minsize=180)  # Nama
        header_frame.grid_columnconfigure(2, weight=1, minsize=200)  # File TTD
        header_frame.grid_columnconfigure(3, weight=1, minsize=200)  # Progress
        header_frame.grid_columnconfigure(4, weight=0, minsize=100)  # Run Button
        
        ctk.CTkLabel(header_frame, text="No", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, sticky="w")
        ctk.CTkLabel(header_frame, text="Nama", font=("Arial", 12, "bold")).grid(row=0, column=1, padx=10, sticky="w")
        ctk.CTkLabel(header_frame, text="File TTD", font=("Arial", 12, "bold")).grid(row=0, column=2, padx=10, sticky="w")
        ctk.CTkLabel(header_frame, text="Progress", font=("Arial", 12, "bold")).grid(row=0, column=3, padx=10, sticky="w")
        ctk.CTkLabel(header_frame, text="Action", font=("Arial", 12, "bold")).grid(row=0, column=4, padx=10, sticky="w")
        
        # Rows
        for i, peserta in enumerate(self.peserta_list, start=1):
            peserta: PesertaModel
            
            row_frame = ctk.CTkFrame(self.content_container, fg_color="#2a2a2a")
            row_frame.pack(fill="x", pady=2)
            
            row_frame.grid_columnconfigure(0, weight=0, minsize=50)
            row_frame.grid_columnconfigure(1, weight=1, minsize=180)
            row_frame.grid_columnconfigure(2, weight=1, minsize=200)
            row_frame.grid_columnconfigure(3, weight=1, minsize=200)
            row_frame.grid_columnconfigure(4, weight=0, minsize=100)
            
            # Column 0: No
            ctk.CTkLabel(row_frame, text=str(i), font=("Arial", 11)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
            
            # Column 1: Nama
            ctk.CTkLabel(row_frame, text=peserta.nama[:25] + "..." if len(peserta.nama) > 25 else peserta.nama, font=("Arial", 11)).grid(row=0, column=1, padx=10, pady=5, sticky="w")
            
            # Column 2: File TTD selector
            file_container = ctk.CTkFrame(row_frame, fg_color="transparent")
            file_container.grid(row=0, column=2, padx=10, pady=5, sticky="ew")
            
            path_label = ctk.CTkLabel(
                file_container,
                text="Belum dipilih",
                font=("Arial", 10),
                text_color="#999999",
                anchor="w"
            )
            path_label.pack(side="left", fill="x", expand=True, padx=(0, 5))
            
            browse_btn = ctk.CTkButton(
                file_container,
                text="📁",
                width=50,
                height=30,
                fg_color="#1a73e8",
                hover_color="#1557b0",
                command=lambda p=peserta, lbl=path_label: self.browse_file(p, lbl)
            )
            browse_btn.pack(side="right")
            
            # Column 3: Progress container
            progress_container = ctk.CTkFrame(row_frame, fg_color="transparent")
            progress_container.grid(row=0, column=3, padx=10, pady=5, sticky="ew")
            
            # Progress bar (hidden initially)
            progress_bar = ctk.CTkProgressBar(
                progress_container,
                width=282,
                height=15,
                corner_radius=5,
                fg_color="#444444",
                progress_color="#4caf50"
            )
            progress_bar.pack(side="right", padx=(0, 5))
            progress_bar.set(0)
            progress_bar.pack_forget()  # Hide initially
            
            # Status label (shown initially)
            status_label = ctk.CTkLabel(
                progress_container,
                text="Ready",
                font=("Arial", 10),
                text_color="#888888"
            )
            status_label.pack(fill="x", expand=True)
            
            # Column 4: Run button
            run_btn = ctk.CTkButton(
                row_frame,
                text="▶️",
                width=70,
                height=30,
                font=("Arial", 12, "bold"),
                fg_color="#34a853",
                hover_color="#2d8e47",
                corner_radius=6,
                command=lambda p=peserta, idx=i: self.run_single_peserta(idx, p)
            )
            run_btn.grid(row=0, column=4, padx=10, pady=5)
            
            # Store references
            peserta._path_label = path_label
            peserta._progress_bar = progress_bar
            peserta._status_label = status_label
            peserta._run_btn = run_btn
            peserta._status = "idle"  # idle | processing | completed | error
            
            # Store row widget
            self.peserta_rows[peserta.id_peserta] = row_frame
    
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
            
            # Update label with truncated filename
            filename = os.path.basename(file_path)
            
            # ✅ TAMBAH: Truncate filename jika terlalu panjang
            max_length = 16  # Adjust sesuai kebutuhan
            if len(filename) > max_length:
                # Pisahkan nama dan ekstensi
                name, ext = os.path.splitext(filename)
                # Truncate name, keep extension
                truncated = name[:max_length - len(ext) - 3] + "..." + ext
                display_name = truncated
            else:
                display_name = filename
            
            path_label.configure(text=display_name, text_color="#4caf50")
    
    def run_single_peserta(self, index, peserta: PesertaModel):
        """Run export for single peserta"""
        # Validation
        if peserta.id_peserta not in self.selected_files:
            messagebox.showwarning("File TTD Belum Dipilih", f"Pilih file TTD untuk {peserta.nama} terlebih dahulu!")
            return
        
        # Check data completeness
        for key, value in peserta.__dict__.items():
            if key != "instansi" and (value is None or value == ""):
                messagebox.showwarning("Data Belum Lengkap", f"Data {peserta.nama} belum lengkap!")
                return
        
        # Update UI
        row_frame = self.peserta_rows[peserta.id_peserta]
        row_frame.grid_columnconfigure(3, weight=0, minsize=200)
        peserta._progress_bar.configure(progress_color="#484848")
        peserta._status_label.destroy()
        peserta._progress_bar.pack(side="right", padx=(8, 5))
        peserta._run_btn.configure(state="disabled", fg_color="#666666")
        
        def export_thread():
            try:
                tanggal_pelatihan = return_format_tanggal(self.sertifikasi_info["tanggal_pelatihan"])
                DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
                OUTPUT_PATH = os.path.join(DOWNLOAD_DIR, f"Dokumen BNSP {tanggal_pelatihan}")
                
                exporter = DokBNSPSingleProcessor()
                
                def on_file_status(peserta_id, status, progress=None):
                    match status:
                        case s if 'running' in s:
                            self.after(0,lambda id=peserta_id, prog=progress:self._on_row_progress(id, prog))

                        case s if 'completed' in s:
                            self.after(0,lambda id=peserta_id:self._on_row_completed(id))

                        case s if 'error' in s:
                            self.after(0,lambda id=peserta_id:self._on_row_error(id))
                
                exporter.process(
                    index,
                    tanggal_pelatihan,
                    peserta,  
                    self.selected_files[peserta.id_peserta],
                    OUTPUT_PATH,
                    on_file_status
                )
                    
            except Exception as e:
                logging.exception(f"Fatal Err ->\n{e}")
                self._on_row_error(peserta.id_peserta)
        
        threading.Thread(target=export_thread, daemon=True).start()
    
    def _on_row_progress(self, peserta_id, value):
        """Update individual row progress"""
        for peserta in self.peserta_list:
            if peserta.id_peserta == peserta_id:
                if value >= 100:
                    peserta._progress_bar.configure(progress_color="#4caf50")  # Green
                elif value >= 50:
                    peserta._progress_bar.configure(progress_color="#2196f3")  # Blue
                else:
                    peserta._progress_bar.configure(progress_color="#ff9800")  # Orange
                    
                peserta._progress_bar.set(value/100)
                break

    def _on_row_completed(self, peserta_id):
        """Handle row completion"""
        for peserta in self.peserta_list:
            if peserta.id_peserta == peserta_id:
                peserta._progress_bar.configure(progress_color="#4caf50")
                peserta._progress_bar.set(1.0)
                break

    def _on_row_error(self, peserta_id):
        """Handle row error"""
        for peserta in self.peserta_list:
            if peserta.id_peserta == peserta_id:
                peserta._progress_bar.configure(progress_color="#d32f2f")
                break
            
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
            logging.exception(f"Fatal Err ->\n{e}")
            self.after(10, lambda: messagebox.showerror(
                "Error",
                f"Gagal ekspor:\n{str(e)}"
            ))
           
    def _on_global_progress(self, value, show_status=True):
        """
        Update progress bar dan percentage label
        
        Args:
            value (float): Progress value 0.0 - 1.0
            show_status (bool): Show progress or hide after completion
        """
        # Show progress container if not visible
        if not self.is_exporting:
            self.show_progress()
        
        # Update progress bar
        self.global_progress_bar.set(value)
        
        # Update percentage text
        percentage = int(value * 100)
        self.progress_label.configure(text=f"{percentage}%")
        
        # Color based on progress
        if value >= 1.0:
            self.global_progress_bar.configure(progress_color="#4caf50")  # Green
            self.progress_label.configure(text_color="#4caf50")
        elif value >= 0.5:
            self.global_progress_bar.configure(progress_color="#2196f3")  # Blue
            self.progress_label.configure(text_color="#ffffff")
        else:
            self.global_progress_bar.configure(progress_color="#ff9800")  # Orange
            self.progress_label.configure(text_color="#ffffff")
        
        self.update_idletasks()
        
        # Auto hide after completion
        if value >= 1.0 and not show_status:
            self.after(1500, self.hide_progress)
            
    def _on_global_completed(self):
        """Show success message in center"""
        # Hide progress
        self.progress_frame.pack_forget()
        
        # # Extract filename from path
        # folder_name = os.path.basename(output_path)
        # parent_folder = os.path.dirname(output_path)
        
        # Update success message
        # self.success_path.configure(text=f"📁 {folder_name}\n📂 {parent_folder}")
        
        # Show success frame
        self.success_frame.pack(fill="both", expand=True)
        
        self.update_idletasks()
        
        # Auto hide and show export button after 4 seconds
        # self.after(4000, self.hide_success_message)

    def _on_global_error(self, msg=None):
        self.global_progress_bar.configure(progress_color="#db1717")
        if msg:
            logging.error(f"[Error] Export gagal! ->\n{msg}")
            return
        logging.error(f"[Error] !!Export gagal!!")
    
    
    # def animate_progress(self, target_value, label_text="", duration=500):
    #     """
    #     Animate progress bar smoothly
        
    #     Args:
    #         target_value (float): Target progress 0.0 - 1.0
    #         label_text (str): Label text
    #         duration (int): Animation duration in ms
    #     """
    #     current = self.global_progress_bar.get()
    #     steps = 20
    #     increment = (target_value - current) / steps
    #     delay = duration // steps
        
    #     def step(count):
    #         if count < steps:
    #             new_value = current + (increment * count)
    #             self.update_progress(new_value, label_text)
    #             self.after(delay, lambda: step(count + 1))
    #         else:
    #             self.update_progress(target_value, label_text)
        
    #     step(0)
 
    def show_progress(self):
        """Show progress bar container"""
        if not self.is_exporting:
            self.is_exporting = True
            self.export_btn.pack_forget()
            self.success_frame.pack_forget()
            self.progress_frame.pack(fill="both", expand=True)
            self.update_idletasks()

    def hide_progress(self):
        """Hide progress bar container"""
        if self.is_exporting:
            self.is_exporting = False
            self.progress_frame.pack_forget()
            self.export_btn.pack(side="right", padx=20)
            self.update_idletasks()

    def reset_ui_state(self):
        """Reset UI state: hide progress/success, show export button"""
        # Hide progress and success frames
        self.progress_frame.pack_forget()
        self.success_frame.pack_forget()
        
        # Reset progress bar
        self.global_progress_bar.set(0)
        self.progress_label.configure(text="0%", text_color="#999999")
        self.global_progress_bar.configure(progress_color="#4caf50")
        
        # Reset exporting state
        self.is_exporting = False
        self.selected_files = {}
        # Show export button if hidden
        if not self.export_btn.winfo_ismapped():
            self.export_btn.pack(side="right", padx=20)
        
        self.update_idletasks()

        
        
    # def hide_success_message(self):
    #     """Hide success message and restore export button"""
    #     self.success_frame.pack_forget()
    #     self.export_btn.pack(side="right", padx=20)
    #     self.is_exporting = False
    #     self.reset_progress()
    #     self.reset_ui_state()
        
    

    # def reset_progress(self):
    #     """Reset progress bar ke state awal"""
    #     self.global_progress_bar.set(0)
    #     self.progress_label.configure(text="0%", text_color="#999999")
    #     self.global_progress_bar.configure(progress_color="#4caf50")
    #     self.hide_progress()
        
    def export_rekap_bnsp(self):
        """Export Rekap BNSP format"""
        def export_thread():
            import pythoncom
            pythoncom.CoInitialize()
            try:
                # Update progress
                self.after(0, lambda: self.update_global_progress(0.2))
                
                tanggal_pelatihan = return_format_tanggal(self.sertifikasi_info["tanggal_pelatihan"])
                data_peserta = []
                for i, peserta in enumerate(self.peserta_list, start=1):
                    gender = peserta._gender_widget.get()
                    data_peserta.append({
                        'no': i,
                        'tuk': NAMA_PERUSAHAAN,
                        'tempat': LOKASI_PERUSAHAAN,
                        'hari': get_text_hari(tanggal_pelatihan),
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
                OUTPUT_PATH = os.path.join(DOWNLOAD_DIR, f"[{tanggal_pelatihan}] Rekap Peserta LSP Energi.xlsx")
                
                # Update progress
                self.after(0, lambda: self._on_global_progress(0.5))
                
                # Export data
                exporter = export_Excel(os.path.join(BASE_DIR, TEMPLATE_REKAP_BNSP))
                success = exporter.export(data_peserta, OUTPUT_PATH)
                
                # Update progress
                self.after(0, lambda: self._on_global_progress(1.0))
                
                # Show result in main thread
                if success:
                    self.after(0, lambda: self._on_global_completed())
                else:
                    # self.after(0, self.reset_progress)
                    self.after(0, lambda: self._on_global_error(None))
                    
            except Exception as e:
                # self.after(0, self.reset_progress)
                self.after(100, self._on_global_error(str(e)))
            finally:
                pythoncom.CoUninitialize()
        
        
        # Run in background thread
        thread = threading.Thread(target=export_thread, daemon=True)
        thread.start()
    
    def export_awl_report(self):
        """Export AWL Report format"""
        def export_thread():
            import pythoncom
            pythoncom.CoInitialize()
            try:
                self.after(0, lambda: self.update_global_progress(0.2))
                
                tanggal_pelatihan = return_format_tanggal(self.sertifikasi_info["tanggal_pelatihan"])
                data_peserta = []
                for i, peserta in enumerate(self.peserta_list, start=1):
                    data_peserta.append({
                        'no': i,
                        'nama_peserta': peserta.nama,
                        'skema': peserta.skema,
                        'nik': peserta.nik,
                        'place_DOB': f"{peserta.tempat_lahir}, {peserta.tanggal_lahir}",
                        'alamat': f"{peserta.alamat}, KEL. {peserta.kelurahan}, KEC. {peserta.kecamatan}, {format_kabupaten(peserta.kabupaten)}, {peserta.provinsi}",
                        'no_hp': peserta.telepon,
                        'pendidikan': peserta.pendidikan,
                        'instansi': peserta.instansi
                    })
                
                DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
                OUTPUT_PATH = os.path.join(DOWNLOAD_DIR, f"[AWL] Peserta BNSP - {tanggal_pelatihan}.xlsx")
                
                self.after(10, lambda: self._on_global_progress(0.5))
                
                # Export data
                exporter = export_Excel(os.path.join(BASE_DIR, TEMPLATE_AWL_REPORT))
                success = exporter.export(data_peserta, OUTPUT_PATH)
                
                self.after(10, lambda: self._on_global_progress(1.0))
                
                if success:
                    self.after(10, lambda: self._on_global_completed())
                else:
                    # self.after(0, self.reset_progress)
                    self.after(10, self._on_global_error(None))
                    
            except Exception as e:
                # self.after(0, self.reset_progress)
                self.after(10, self._on_global_error, str(e))
            finally:
                pythoncom.CoUninitialize()
        
        thread = threading.Thread(target=export_thread, daemon=True)
        thread.start()
    
    def export_dokumen_bnsp(self):
        """Export Dokumen BNSP format"""
        # Check if all files selected
        missing_files = []
        missing_data = []
        for peserta in self.peserta_list:
            peserta: PesertaModel
            if peserta.id_peserta not in self.selected_files:
                missing_files.append(peserta.nama)
            
            for key, value in peserta.__dict__.items():
                if key != "instansi" and (value is None or value == ""):
                    missing_data.append(peserta.nama)
                    break
        
        missing_files = list(dict.fromkeys(missing_files))
        missing_data = list(dict.fromkeys(missing_data))

        if missing_files or missing_data:
            pesan = ""

            if missing_files:
                pesan += (
                    "⚠️ File TTD belum dipilih untuk:\n\n"
                    + "\n".join(missing_files[:5])
                )
                if len(missing_files) > 5:
                    pesan += f"\n... dan {len(missing_files) - 5} lainnya"
                pesan += "\n\n"

            if missing_data:
                pesan += (
                    "📄 Data belum lengkap untuk:\n\n"
                    + "\n".join(missing_data[:5])
                )
                if len(missing_data) > 5:
                    pesan += f"\n... dan {len(missing_data) - 5} lainnya"

            messagebox.showwarning(
                "Data Peserta Belum Lengkap",
                pesan
            )
            return
        
        for peserta in self.peserta_list:
            row_frame = self.peserta_rows[peserta.id_peserta]
            row_frame.grid_columnconfigure(3, weight=0, minsize=200)
            peserta._progress_bar.pack(side="right", padx=(8, 5))
            peserta._progress_bar.set(0)
            peserta._status_label.destroy()
            peserta._progress_bar.configure(progress_color="#484848")
            peserta._run_btn.configure(state="disabled", fg_color="#666666")
            
        exporter = DokBNSPBatchProcessor()
        def export_thread():
            try:
                # Show progress
                self.after(0, lambda: self._on_global_progress(0))
                
                tanggal_pelatihan = return_format_tanggal(self.sertifikasi_info["tanggal_pelatihan"])
                
                DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
                OUTPUT_PATH = os.path.join(DOWNLOAD_DIR, f"Dokumen BNSP {tanggal_pelatihan}")
                        
                # Export data
                progress_map = {p.id_peserta: 0 for p in self.peserta_list}
                completed_count = 0
                total_peserta = len(self.peserta_list)
                def on_single_status(peserta_id, status, progress=None):
                    nonlocal completed_count
                    match status:
                        
                        case s if 'running' in s:
                            progress_map[peserta_id] = progress
                        
                            self.after(0, lambda id=peserta_id, prog=progress: self._on_row_progress(id, prog))
                            
                            total_progress = sum(progress_map.values())
                            avg_progress = total_progress / (total_peserta * 100)  
                            self.after(0, lambda avg=avg_progress: self._on_global_progress(avg))

                        case s if 'completed' in s:
                            completed_count += 1
                            progress_map[peserta_id] = 100  
                            
                            self.after(0, lambda id=peserta_id: self._on_row_completed(id))
                            
                            avg_progress = sum(progress_map.values()) / (total_peserta * 100)
                            self.after(0, lambda avg=avg_progress: self._on_global_progress(avg))

                        case s if 'error' in s:
                            self.after(0,lambda id=peserta_id: self._on_row_error(id))
                                                                
                def on_global_status(status):
                    match status:
                        case s if 'completed' in s:
                            self.after(0, lambda: self._on_global_progress(1.0))
                            self.after(300, lambda: self._on_global_completed())

                        case s if 'error' in s:
                            # self.after(0, self.reset_progress)
                            self.after(0, lambda: self._on_global_error(None))
                            

                exporter.batch_process(
                    tanggal_pelatihan, 
                    self.peserta_list, 
                    self.selected_files, 
                    OUTPUT_PATH,
                    on_single_status,
                    on_global_status,
                )
                
            except Exception as e:
                self.after(0, lambda: self._on_global_error(str(e)))

            
            finally:
                exporter.cleanup()
        
        # Run in background thread
        thread = threading.Thread(target=export_thread, daemon=True)
        thread.start()