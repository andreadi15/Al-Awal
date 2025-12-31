import customtkinter as ctk
from tkinter import messagebox
import re
from pages.peserta_model import PesertaModel


class InputPesertaPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#2a2a2a")
        
        # Data untuk combobox
        self.skema_options = ["Skema A", "Skema B", "Skema C", "Skema D"]
        self.pendidikan_options = [
            "SD", "SMP", "SMA/SMK", "D3", "S1", "S2", "S3"
        ]
        self.sertifikasi_options = ["BNSP", "CEPU", "IADC"]
        
        # List untuk menyimpan semua peserta
        self.list_peserta = []
        
        # Index peserta saat ini (0-based)
        self.current_index = 0
        
        # NIK placeholder
        self.nik_placeholder = "─" * 16
        self.nik_value = ""
        
        self.create_widgets()
        self.update_navigation_buttons()
        self.update_sertifikasi_state()
    
    def create_widgets(self):
        # Container utama
        main_container = ctk.CTkFrame(self, fg_color="#2a2a2a")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = ctk.CTkLabel(
            main_container,
            text="📝 INPUT DATA PESERTA",
            font=("Arial", 28, "bold"),
            text_color="#1a73e8"
        )
        header.pack(pady=(0, 10))
        
        # Container untuk data peserta yang sudah diinput (initially hidden)
        self.data_container_wrapper = ctk.CTkFrame(main_container, fg_color="transparent")
        
        # Header data container dengan delete all button
        data_header = ctk.CTkFrame(self.data_container_wrapper, fg_color="transparent")
        data_header.pack(fill="x", pady=(0, 5))
        
        data_label = ctk.CTkLabel(
            data_header,
            text="Data Peserta Tersimpan:",
            font=("Arial", 14, "bold"),
            text_color="#ffffff"
        )
        data_label.pack(side="left")
        
        delete_all_btn = ctk.CTkButton(
            data_header,
            text="🗑️ Delete All",
            font=("Arial", 12, "bold"),
            fg_color="#dc3545",
            hover_color="#c82333",
            height=30,
            width=120,
            corner_radius=8,
            command=self.delete_all_data
        )
        delete_all_btn.pack(side="right")
        
        # Scrollable frame untuk button data peserta
        self.data_scroll_frame = ctk.CTkScrollableFrame(
            self.data_container_wrapper,
            fg_color="#333333",
            height=100,
            scrollbar_button_color="#888888",
            scrollbar_button_hover_color="#666666"
        )
        self.data_scroll_frame.pack(fill="x", pady=(0, 15))
        
        # Configure grid untuk data buttons
        for i in range(10):  # 10 kolom
            self.data_scroll_frame.grid_columnconfigure(i, weight=1, minsize=100)
        
        # Form Container dengan scrollbar custom
        form_container = ctk.CTkScrollableFrame(
            main_container,
            fg_color="#2a2a2a",
            scrollbar_button_color="#888888",
            scrollbar_button_hover_color="#666666"
        )
        form_container.pack(fill="both", expand=True)
        
        form_frame = ctk.CTkFrame(form_container, fg_color="#333333", corner_radius=15)
        form_frame.pack(fill="both", expand=True, padx=50)
        
        # Form content dengan padding
        form_content = ctk.CTkFrame(form_frame, fg_color="transparent")
        form_content.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Header row dengan Sertifikasi dan Counter
        header_row = ctk.CTkFrame(form_content, fg_color="transparent")
        header_row.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        header_row.grid_columnconfigure(1, weight=1)
        
        # Sertifikasi combo box (kiri)
        sertifikasi_label = ctk.CTkLabel(
            header_row,
            text="Sertifikasi:",
            font=("Arial", 14, "bold"),
            text_color="#ffffff"
        )
        sertifikasi_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        self.sertifikasi_combo = ctk.CTkComboBox(
            header_row,
            font=("Arial", 13),
            height=40,
            corner_radius=8,
            values=self.sertifikasi_options,
            fg_color="#2a2a2a",
            border_color="#1a73e8",
            button_color="#1a73e8",
            button_hover_color="#1557b0",
            dropdown_fg_color="#333333",
            width=150
        )
        self.sertifikasi_combo.grid(row=0, column=1, sticky="w")
        self.sertifikasi_combo.set(self.sertifikasi_options[0])
        
        # Counter peserta (kanan)
        self.counter_label = ctk.CTkLabel(
            header_row,
            text="Peserta #1",
            font=("Arial", 16, "bold"),
            text_color="#ffffff",
            fg_color="#1a73e8",
            corner_radius=8,
            padx=20,
            pady=5
        )
        self.counter_label.grid(row=0, column=2, sticky="e")
        
        # Row tracking
        current_row = 1
        
        # 1. Skema (ComboBox)
        self.skema_combo = self.create_form_row(
            form_content, current_row, 
            "Skema", "combobox", 
            options=self.skema_options
        )
        current_row += 1
        
        # 2. Nama Lengkap
        self.nama_entry = self.create_form_row(
            form_content, current_row, 
            "Nama Lengkap", "entry",
            placeholder="Masukkan nama lengkap"
        )
        current_row += 1
        
        # 3. NIK (Custom dengan placeholder ─)
        nik_label = ctk.CTkLabel(
            form_content,
            text="NIK",
            font=("Arial", 14, "bold"),
            anchor="w",
            text_color="#ffffff"
        )
        nik_label.grid(row=current_row, column=0, sticky="w", pady=12, padx=(0, 20))
        
        self.nik_entry = ctk.CTkEntry(
            form_content,
            font=("Arial", 13),
            height=40,
            corner_radius=8,
            fg_color="#2a2a2a",
            border_color="#1a73e8"
        )
        self.nik_entry.grid(row=current_row, column=1, sticky="ew", pady=12)
        self.nik_entry.insert(0, self.format_nik_display(self.nik_value))
        self.nik_entry.bind("<KeyPress>", self.handle_nik_input)
        self.nik_entry.bind("<FocusIn>", lambda e: self.nik_entry.configure(cursor="none"))
        self.nik_entry.bind("<FocusOut>", lambda e: self.nik_entry.configure(cursor=""))
        current_row += 1
        
        # 4. Tempat Lahir
        self.tempat_lahir_entry = self.create_form_row(
            form_content, current_row, 
            "Tempat Lahir", "entry",
            placeholder="Kota/Kabupaten kelahiran"
        )
        current_row += 1
        
        # 5. Tanggal Lahir (dengan auto-format)
        self.tanggal_lahir_entry = self.create_form_row(
            form_content, current_row, 
            "Tanggal Lahir", "entry",
            placeholder="DD-MM-YYYY"
        )
        self.tanggal_lahir_entry.bind("<KeyRelease>", self.format_tanggal_lahir)
        current_row += 1
        
        # 6. Alamat (Text area)
        self.alamat_text = self.create_form_row(
            form_content, current_row, 
            "Alamat", "textbox",
            placeholder="Alamat lengkap"
        )
        current_row += 1
        
        # 7. Kelurahan
        self.kelurahan_entry = self.create_form_row(
            form_content, current_row, 
            "Kelurahan", "entry",
            placeholder="Nama kelurahan"
        )
        current_row += 1
        
        # 8. Kecamatan
        self.kecamatan_entry = self.create_form_row(
            form_content, current_row, 
            "Kecamatan", "entry",
            placeholder="Nama kecamatan"
        )
        current_row += 1
        
        # 9. Kabupaten
        self.kabupaten_entry = self.create_form_row(
            form_content, current_row, 
            "Kabupaten", "entry",
            placeholder="Nama kabupaten/kota"
        )
        current_row += 1
        
        # 10. Provinsi
        self.provinsi_entry = self.create_form_row(
            form_content, current_row, 
            "Provinsi", "entry",
            placeholder="Nama provinsi"
        )
        current_row += 1
        
        # 11. No. Telepon
        self.telepon_entry = self.create_form_row(
            form_content, current_row, 
            "No. Telepon", "entry",
            placeholder="08xxxxxxxxxx"
        )
        current_row += 1
        
        # 12. Pendidikan Terakhir
        self.pendidikan_combo = self.create_form_row(
            form_content, current_row, 
            "Pendidikan Terakhir", "combobox",
            options=self.pendidikan_options
        )
        current_row += 1
        
        # Reset button (di bawah pendidikan terakhir)
        reset_frame = ctk.CTkFrame(form_content, fg_color="transparent")
        reset_frame.grid(row=current_row, column=0, columnspan=2, sticky="e", pady=(10, 20))
        
        reset_link = ctk.CTkLabel(
            reset_frame,
            text="🔄 Reset Form",
            font=("Arial", 13, "underline"),
            text_color="#dc3545",
            cursor="hand2"
        )
        reset_link.pack()
        reset_link.bind("<Button-1>", lambda e: self.reset_form())
        
        current_row += 1
        
        # Button Container dengan grid layout
        button_frame = ctk.CTkFrame(form_content, fg_color="transparent")
        button_frame.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=(10, 10))
        
        # Configure grid untuk responsive buttons
        for i in range(3):
            button_frame.grid_columnconfigure(i, weight=1, uniform="buttons")
        
        # Tombol Prev
        self.prev_btn = ctk.CTkButton(
            button_frame,
            text="⬅️ Prev",
            font=("Arial", 16, "bold"),
            fg_color="#6c757d",
            hover_color="#5a6268",
            height=50,
            corner_radius=10,
            command=self.previous_peserta
        )
        self.prev_btn.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Tombol Next
        self.next_btn = ctk.CTkButton(
            button_frame,
            text="Next ➡️",
            font=("Arial", 16, "bold"),
            fg_color="#28a745",
            hover_color="#218838",
            height=50,
            corner_radius=10,
            command=self.next_peserta
        )
        self.next_btn.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Tombol Save
        self.save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Save",
            font=("Arial", 16, "bold"),
            fg_color="#1a73e8",
            hover_color="#1557b0",
            height=50,
            corner_radius=10,
            command=self.save_all_data
        )
        self.save_btn.grid(row=0, column=2, sticky="ew", padx=5, pady=5)
    
    def create_form_row(self, parent, row, label_text, input_type, **kwargs):
        """Helper untuk membuat baris form"""
        # Label
        label = ctk.CTkLabel(
            parent,
            text=label_text,
            font=("Arial", 14, "bold"),
            anchor="w",
            text_color="#ffffff"
        )
        label.grid(row=row, column=0, sticky="w", pady=12, padx=(0, 20))
        
        # Input widget
        if input_type == "entry":
            widget = ctk.CTkEntry(
                parent,
                font=("Arial", 13),
                height=40,
                corner_radius=8,
                placeholder_text=kwargs.get("placeholder", ""),
                fg_color="#2a2a2a",
                border_color="#1a73e8"
            )
            widget.grid(row=row, column=1, sticky="ew", pady=12)
            
        elif input_type == "combobox":
            widget = ctk.CTkComboBox(
                parent,
                font=("Arial", 13),
                height=40,
                corner_radius=8,
                values=kwargs.get("options", []),
                fg_color="#2a2a2a",
                border_color="#1a73e8",
                button_color="#1a73e8",
                button_hover_color="#1557b0",
                dropdown_fg_color="#333333"
            )
            widget.grid(row=row, column=1, sticky="ew", pady=12)
                
        elif input_type == "textbox":
            widget = ctk.CTkTextbox(
                parent,
                font=("Arial", 13),
                height=80,
                corner_radius=8,
                fg_color="#2a2a2a",
                border_color="#1a73e8"
            )
            widget.grid(row=row, column=1, sticky="ew", pady=12)
        
        # Configure column weight
        parent.grid_columnconfigure(1, weight=1)
        
        return widget
    
    def format_nik_display(self, nik_value):
        """Format NIK dengan spasi setiap 4 digit"""
        # Gabungkan NIK value dengan placeholder
        full_nik = nik_value + self.nik_placeholder[len(nik_value):]
        
        # Tambahkan spasi setiap 4 karakter
        formatted = ""
        for i, char in enumerate(full_nik):
            if i > 0 and i % 4 == 0:
                formatted += " "
            formatted += char
        
        return formatted
    
    def handle_nik_input(self, event):
        """Handle input NIK dengan format ─ placeholder"""
        # Block semua key kecuali angka dan backspace
        if event.keysym == "BackSpace":
            if len(self.nik_value) > 0:
                self.nik_value = self.nik_value[:-1]
        elif event.char.isdigit() and len(self.nik_value) < 16:
            self.nik_value += event.char
        else:
            return "break"  # Block input lain
        
        # Update display dengan format spasi
        display = self.format_nik_display(self.nik_value)
        self.nik_entry.delete(0, "end")
        self.nik_entry.insert(0, display)
        
        return "break"  # Prevent default behavior
    
    def format_tanggal_lahir(self, event):
        """Auto-format tanggal lahir: DD-MM-YYYY"""
        entry = event.widget
        text = entry.get()
        
        # Hapus semua karakter non-digit
        digits = re.sub(r'\D', '', text)
        
        # Batasi maksimal 8 digit
        digits = digits[:8]
        
        # Format dengan strip
        formatted = ""
        for i, digit in enumerate(digits):
            if i == 2 or i == 4:
                formatted += "-"
            formatted += digit
        
        # Update entry jika berbeda
        if formatted != text:
            cursor_pos = entry.index("insert")
            entry.delete(0, "end")
            entry.insert(0, formatted)
            if len(formatted) > len(text):
                cursor_pos += 1
            entry.icursor(cursor_pos)
    
    def validate_current_form(self):
        """Validasi form peserta saat ini"""
        errors = []
        
        # Validasi Sertifikasi
        if not self.sertifikasi_combo.get():
            errors.append("Sertifikasi harus dipilih")
        
        # Validasi Skema
        if not self.skema_combo.get():
            errors.append("Skema harus dipilih")
        
        # Validasi Nama
        if not self.nama_entry.get().strip():
            errors.append("Nama lengkap harus diisi")
        
        # Validasi NIK (harus 16 digit)
        if len(self.nik_value) != 16:
            errors.append("NIK harus 16 digit")
        
        # Validasi Tempat Lahir
        if not self.tempat_lahir_entry.get().strip():
            errors.append("Tempat lahir harus diisi")
        
        # Validasi Tanggal Lahir
        tanggal = self.tanggal_lahir_entry.get().strip()
        if not tanggal:
            errors.append("Tanggal lahir harus diisi")
        elif not re.match(r'^\d{2}-\d{2}-\d{4}$', tanggal):
            errors.append("Format tanggal lahir: DD-MM-YYYY")
        
        # Validasi Alamat
        if not self.alamat_text.get("1.0", "end").strip():
            errors.append("Alamat harus diisi")
        
        # Validasi wilayah
        if not self.kelurahan_entry.get().strip():
            errors.append("Kelurahan harus diisi")
        if not self.kecamatan_entry.get().strip():
            errors.append("Kecamatan harus diisi")
        if not self.kabupaten_entry.get().strip():
            errors.append("Kabupaten harus diisi")
        if not self.provinsi_entry.get().strip():
            errors.append("Provinsi harus diisi")
        
        # Validasi No. Telepon
        telepon = self.telepon_entry.get().strip()
        if not telepon:
            errors.append("No. telepon harus diisi")
        elif not telepon.isdigit():
            errors.append("No. telepon harus berupa angka")
        
        # Validasi Pendidikan
        if not self.pendidikan_combo.get():
            errors.append("Pendidikan terakhir harus dipilih")
        
        return errors
    
    def get_current_form_data(self):
        """Ambil data dari form saat ini"""
        peserta = PesertaModel(
            sertifikasi=self.sertifikasi_combo.get(),
            skema=self.skema_combo.get(),
            nama=self.nama_entry.get().strip(),
            nik=self.nik_value,
            tempat_lahir=self.tempat_lahir_entry.get().strip(),
            tanggal_lahir=self.tanggal_lahir_entry.get().strip(),
            alamat=self.alamat_text.get("1.0", "end").strip(),
            kelurahan=self.kelurahan_entry.get().strip(),
            kecamatan=self.kecamatan_entry.get().strip(),
            kabupaten=self.kabupaten_entry.get().strip(),
            provinsi=self.provinsi_entry.get().strip(),
            telepon=self.telepon_entry.get().strip(),
            pendidikan=self.pendidikan_combo.get()
        )
        return peserta
    
    def load_form_data(self, peserta):
        """Load data peserta ke form"""
        self.sertifikasi_combo.set(peserta.sertifikasi)
        self.skema_combo.set(peserta.skema)
        self.nama_entry.delete(0, "end")
        self.nama_entry.insert(0, peserta.nama)
        
        # Load NIK dengan format
        self.nik_value = peserta.nik
        display = self.format_nik_display(self.nik_value)
        self.nik_entry.delete(0, "end")
        self.nik_entry.insert(0, display)
        
        self.tempat_lahir_entry.delete(0, "end")
        self.tempat_lahir_entry.insert(0, peserta.tempat_lahir)
        self.tanggal_lahir_entry.delete(0, "end")
        self.tanggal_lahir_entry.insert(0, peserta.tanggal_lahir)
        self.alamat_text.delete("1.0", "end")
        self.alamat_text.insert("1.0", peserta.alamat)
        self.kelurahan_entry.delete(0, "end")
        self.kelurahan_entry.insert(0, peserta.kelurahan)
        self.kecamatan_entry.delete(0, "end")
        self.kecamatan_entry.insert(0, peserta.kecamatan)
        self.kabupaten_entry.delete(0, "end")
        self.kabupaten_entry.insert(0, peserta.kabupaten)
        self.provinsi_entry.delete(0, "end")
        self.provinsi_entry.insert(0, peserta.provinsi)
        self.telepon_entry.delete(0, "end")
        self.telepon_entry.insert(0, peserta.telepon)
        self.pendidikan_combo.set(peserta.pendidikan)
    
    def reset_form(self):
        """Reset semua input field"""
        self.skema_combo.set("")
        self.nama_entry.delete(0, "end")
        
        # Reset NIK
        self.nik_value = ""
        self.nik_entry.delete(0, "end")
        self.nik_entry.insert(0, self.format_nik_display(self.nik_value))
        
        self.tempat_lahir_entry.delete(0, "end")
        self.tanggal_lahir_entry.delete(0, "end")
        self.alamat_text.delete("1.0", "end")
        self.kelurahan_entry.delete(0, "end")
        self.kecamatan_entry.delete(0, "end")
        self.kabupaten_entry.delete(0, "end")
        self.provinsi_entry.delete(0, "end")
        self.telepon_entry.delete(0, "end")
        self.pendidikan_combo.set("")
        
        # Clear error messages
        # for label
        
        
        
        
        
        
        
        
        
        
        
        
        # ini bekas input peserta
    def format_nik_display(self, nik_value):
        """Format NIK dengan spasi setiap 4 digit"""
        # Gabungkan NIK value dengan placeholder
        full_nik = nik_value + self.nik_placeholder[len(nik_value):]
        
        # Tambahkan spasi setiap 4 karakter
        formatted = ""
        for i, char in enumerate(full_nik):
            if i > 0 and i % 4 == 0:
                formatted += " "
            formatted += char
        
        return formatted
    
    def handle_nik_input(self, event):
        """Handle input NIK dengan format ─ placeholder"""
        # Block semua key kecuali angka dan backspace
        if event.keysym == "BackSpace":
            if len(self.nik_value) > 0:
                self.nik_value = self.nik_value[:-1]
        elif event.char.isdigit() and len(self.nik_value) < 16:
            self.nik_value += event.char
        else:
            return "break"  # Block input lain
        
        # Update display dengan format spasi
        display = self.format_nik_display(self.nik_value)
        self.nik_entry.delete(0, "end")
        self.nik_entry.insert(0, display)
        
        return "break"  # Prevent default behavior
    