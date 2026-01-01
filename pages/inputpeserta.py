import customtkinter as ctk
from tkinter import messagebox
import re
from pages.peserta_model import PesertaModel
from components import peserta_validator,create_entry,form_row,nik_entry,peserta_list_panel
from config import SERTIFIKASI_OPTIONS,SKEMA_OPTIONS,PENDIDIKAN_OPTIONS

class InputPesertaPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#2a2a2a")

        self.entries = {}
        self.error_labels = {}
        # List untuk menyimpan semua peserta
        self.list_peserta = []
        
        # Index peserta saat ini (0-based)
        self.current_index = 0  
        
        self.DEFAULT_BORDER_COLOR = "#1a73e8"
        self.ERROR_BORDER_COLOR = "#ff4d4f"
        
        self._build_layout()
        self._build_container_data()
        self._build_form()
        self.refresh_UI_Form()
    
    def _build_layout(self):
        # Container utama
        self.main_container = ctk.CTkScrollableFrame(
            self, 
            fg_color="#2a2a2a",
            scrollbar_button_color="#888888",
            scrollbar_button_hover_color="#666666")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        self.main_container.bind_all("<MouseWheel>", self._on_mousewheel)

        
        # Header
        self.header_label = ctk.CTkLabel(
            self.main_container,
            text="📝 INPUT DATA PESERTA",
            font=("Arial", 28, "bold"),
            text_color="#1a73e8"
        )
        self.header_label.pack(pady=(0, 10))
        
        self.form_container = ctk.CTkFrame(
            self.main_container,
            fg_color="#2a2a2a"
        )
        self.form_container.pack(fill="both", expand=True)
        
    def _build_container_data(self):
        # Container untuk data peserta yang sudah diinput (initially hidden)
        self.data_container_wrapper = ctk.CTkFrame(self.main_container, fg_color="transparent")
        
        # Header data container dengan delete all button
        self.data_header = ctk.CTkFrame(self.data_container_wrapper, fg_color="transparent")
        self.data_header.pack(fill="x", pady=(0, 5))
        
        data_label = ctk.CTkLabel(
            self.data_header,
            text="Data Peserta Tersimpan:",
            font=("Arial", 14, "bold"),
            text_color="#ffffff"
        )
        data_label.pack(side="left")
        
        delete_all_btn = ctk.CTkButton(
            self.data_header,
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
            
    # =======================
    # FORM
    # =======================
    def _build_form(self):
        self.form_frame = ctk.CTkFrame(self.form_container, fg_color="#333333", corner_radius=15)
        self.form_frame.pack(fill="both", expand=True, padx=50)
        
        # Form content dengan padding
        form_content = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        form_content.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Header row dengan Sertifikasi dan Counter
        header_row = ctk.CTkFrame(form_content, fg_color="transparent")
        header_row.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        header_row.grid_columnconfigure(1, weight=1)
        
        # Sertifikasi combo box (kiri)
        sertifikasi_label = ctk.CTkLabel(header_row, text="Sertifikasi:", font=("Arial", 14, "bold"), text_color="#ffffff")
        sertifikasi_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        entry = create_entry.createEntry(header_row, "combobox", options=SERTIFIKASI_OPTIONS, width=150)
        self.entries["sertifikasi"] = entry.widget
        self.entries["sertifikasi"].grid(row=0, column=1, sticky="w")
        self.entries["sertifikasi"].set(SERTIFIKASI_OPTIONS[0])
        
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
        entry = create_entry.createEntry(form_content, "combobox", options=SKEMA_OPTIONS)
        self.entries["skema"] = entry.widget
        form_row.FormRow(form_content, current_row, "Skema", self.entries["skema"])
        current_row += 2
        
        # 2. Nama Lengkap
        entry = create_entry.createEntry(form_content, "entry", placeholder="Masukkan nama lengkap")
        self.entries["nama"] = entry.widget
        form_row.FormRow(form_content, current_row, "Nama Lengkap", self.entries["nama"])
        current_row += 2
        
        # 3. NIK (Custom dengan placeholder ─)   
        entry = create_entry.createEntry(form_content, "nik", placeholder="")
        self.entries["nik"] = entry.widget
        form_row.FormRow(form_content, current_row, "NIK", self.entries["nik"])
        current_row += 2
        
        # 4. Tempat Lahir
        entry = create_entry.createEntry(form_content, "entry", placeholder="Tempat lahir")
        self.entries["tempat_lahir"] = entry.widget
        form_row.FormRow(form_content, current_row, "Tempat Lahir", self.entries["tempat_lahir"])
        current_row += 2
        
        # 5. Tanggal Lahir (dengan auto-format)
        entry = create_entry.createEntry(form_content, "entry", placeholder="DD-MM-YYYY")
        self.entries["tanggal_lahir"] = entry.widget
        form_row.FormRow(form_content,current_row,"Tanggal Lahir",self.entries["tanggal_lahir"])
        self.entries["tanggal_lahir"].bind("<KeyPress>", self.format_tanggal_lahir)
        current_row += 2
        
        # 6. Alamat (Text area)
        entry = create_entry.createEntry(form_content, "textbox", placeholder="Alamat lengkap")
        self.entries["alamat"] = entry.widget
        form_row.FormRow(form_content, current_row, "Alamat", self.entries["alamat"])
        current_row += 2
        
        # 7. Kelurahan
        entry = create_entry.createEntry(form_content, "entry", placeholder="Nama kelurahan")
        self.entries["kelurahan"] = entry.widget
        form_row.FormRow(form_content, current_row, "Kelurahan", self.entries["kelurahan"])
        current_row += 2
        
        # 8. Kecamatan
        entry = create_entry.createEntry(form_content, "entry", placeholder="Nama kecamatan")
        self.entries["kecamatan"] = entry.widget
        form_row.FormRow(form_content, current_row, "Kecamatan", self.entries["kecamatan"])
        current_row += 2
        
        # 9. Kabupaten
        entry = create_entry.createEntry(form_content, "entry", placeholder="Nama kabupaten/kota")
        self.entries["kabupaten"] = entry.widget
        form_row.FormRow(form_content, current_row, "Kabupaten", self.entries["kabupaten"])
        current_row += 2
        
        # 10. Provinsi
        entry = create_entry.createEntry(form_content,"entry", placeholder="Nama provinsi")
        self.entries["provinsi"] = entry.widget
        form_row.FormRow(form_content, current_row, "Provinsi", self.entries["provinsi"])
        current_row += 2
        
        # 11. No. Telepon
        entry = create_entry.createEntry(form_content, "entry",placeholder="08xxxxxxxxxx")
        self.entries["telepon"] = entry.widget
        form_row.FormRow(form_content, current_row, "No. Telepon", self.entries["telepon"])
        self.entries["telepon"].bind("<KeyPress>", self.format_no_telepon)
        current_row += 2
        
        # 12. Pendidikan Terakhir
        entry = create_entry.createEntry(form_content, "combobox",options=PENDIDIKAN_OPTIONS)
        self.entries["pendidikan"] = entry.widget
        form_row.FormRow(form_content, current_row, "Pendidikan Terakhir", self.entries["pendidikan"])
        current_row += 2
        
        # 13. Instansi
        entry = create_entry.createEntry(form_content, "entry", placeholder="Nama Instansi")
        self.entries["instansi"] = entry.widget
        form_row.FormRow(form_content, current_row, "Instansi", self.entries["instansi"])
        current_row += 2
        
        for w in self.entries.values():
            w.bind("<FocusIn>", lambda e, widget=w: self.scroll_to_widget(widget))
        
        # Reset button (di bawah pendidikan terakhir)
        reset_frame = ctk.CTkFrame(form_content, fg_color="transparent")
        reset_frame.grid(row=current_row, column=0, columnspan=2, sticky="e", pady=(10, 20))
        
        reset_link = ctk.CTkLabel(
            reset_frame,
            text="🔄 Reset Form",
            font=("Arial", 13, "underline"),
            text_color="#ff051e",
            cursor="hand2"
        )
        reset_link.pack()
        reset_link.bind("<Button-1>", lambda e: self.clear_form())
        
        current_row += 1
        
        # Button Container dengan grid layout
        button_frame = ctk.CTkFrame(form_content, fg_color="transparent")
        button_frame.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=(10, 10))
        
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
        
        # Tombol Save (di tengah, col 1)
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
        self.save_btn.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Tombol Next (di kanan, col 2)
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
        self.next_btn.grid(row=0, column=2, sticky="ew", padx=5, pady=5)
        
        
        # Configure grid untuk responsive buttons (3 kolom)
        for i in range(3):
            button_frame.grid_columnconfigure(i, weight=1, uniform="buttons")
        
    # def format_tanggal_lahir(self, event):
    #     """Auto-format tanggal lahir: DD-MM-YYYY"""
    #     entry = event.widget
    #     text = entry.get()
        
    #     # Hapus semua karakter non-digit
    #     digits = re.sub(r'\D', '', text)
        
    #     # Batasi maksimal 8 digit
    #     digits = digits[:8]
        
    #     # Format dengan strip
    #     formatted = ""
    #     for i, digit in enumerate(digits):
    #         if i == 2 or i == 4:
    #             formatted += "-"
    #         formatted += digit
        
    #     # Update entry jika berbeda
    #     if formatted != text:
    #         cursor_pos = entry.index("insert")
    #         entry.delete(0, "end")
    #         entry.insert(0, formatted)
    #         if len(formatted) > len(text):
    #             cursor_pos += 1
    #         entry.icursor(cursor_pos)

    # =======================
    # LOGIC
    # =======================
    def format_tanggal_lahir(self, event):
        """Handler untuk input tanggal lahir - KeyPress"""
        entry = event.widget
        current_text = entry.get()
        
        # Ambil hanya digit dari text saat ini
        current_digits = re.sub(r'\D', '', current_text)
        
        # Handle Backspace
        if event.keysym == "BackSpace":
            if len(current_digits) > 0:
                current_digits = current_digits[:-1]
            else:
                return "break"
        # Handle input digit
        elif event.char.isdigit():
            # Cek apakah sudah mencapai batas 8 digit
            if len(current_digits) >= 8:
                return "break"
            current_digits += event.char
        else:
            # Karakter selain digit atau backspace, block
            return "break"
        
        # Format dengan strip: DD-MM-YYYY
        formatted = ""
        for i, digit in enumerate(current_digits):
            if i == 2 or i == 4:
                formatted += "-"
            formatted += digit
        
        # Update entry
        entry.delete(0, "end")
        entry.insert(0, formatted)
        
        return "break"
    
    def format_no_telepon(self, event):
        """Handler untuk input telepon - hanya angka"""
        entry = event.widget
        current_text = entry.get()
        
        # Handle Backspace
        if event.keysym == "BackSpace":
            return  # Allow backspace
        # Hanya izinkan digit
        elif event.char.isdigit():
            return  # Allow digit
        else:
            # Block karakter selain digit
            return "break"
        
    def _on_mousewheel(self, event):
        # scroll lebih cepat  (angka 2 bisa jadi 3, 4, 5 sesuai rasa)
        self.main_container._parent_canvas.yview_scroll(
            int(-1 * (event.delta/120) * 50),  # scroll multiplier 3x
            "units")
        
    def scroll_to_widget(self, widget):
        """Scroll otomatis ke widget saat mendapat focus"""
        try:
            # Pastikan semua widget sudah terupdate
            widget.update_idletasks()
            self.main_container.update_idletasks()
            
            # Dapatkan canvas dari scrollable frame
            canvas = self.main_container._parent_canvas
            
            # Dapatkan posisi widget relatif terhadap form_frame
            widget_y = widget.winfo_rooty() - self.form_frame.winfo_rooty()
            
            # Dapatkan tinggi viewport (area yang terlihat)
            canvas_height = canvas.winfo_height()
            
            # Dapatkan total tinggi konten
            canvas.update_idletasks()
            bbox = canvas.bbox("all")
            if not bbox:
                return
            content_height = bbox[3] - bbox[1]
            
            if content_height <= canvas_height:
                # Konten muat semua, tidak perlu scroll
                return
            
            # Hitung posisi scroll yang ideal
            # Taruh widget di tengah viewport dengan offset 100px dari atas
            target_y = widget_y - 100
            
            # Normalisasi ke range 0.0 - 1.0
            scroll_position = target_y / content_height
            
            # Batasi antara 0.0 dan 1.0
            scroll_position = max(0.0, min(1.0, scroll_position))
            
            # Terapkan scroll
            canvas.yview_moveto(scroll_position)
            
        except Exception as e:
            # Abaikan error untuk menghindari crash
            print(f"Scroll error: {e}")
            pass

    def collect_form(self):
        """Ambil data dari form saat ini"""        
        return PesertaModel(
            sertifikasi=self.entries["sertifikasi"].get(),
            skema=self.entries["skema"].get(),
            nama=self.entries["nama"].get(),
            nik=self.entries["nik"].get_value(),
            tempat_lahir=self.entries["tempat_lahir"].get(),
            tanggal_lahir=self.entries["tanggal_lahir"].get(),
            alamat=self.entries["alamat"].get("1.0","end"),
            kelurahan=self.entries["kelurahan"].get(),
            kecamatan=self.entries["kecamatan"].get(),
            kabupaten=self.entries["kabupaten"].get(),
            provinsi=self.entries["provinsi"].get(),
            telepon=self.entries["telepon"].get(),
            pendidikan=self.entries["pendidikan"].get(),
            instansi=self.entries["instansi"].get()
        )
 
    def load_form(self, peserta: PesertaModel):
        """Load data peserta ke form"""
        self.entries["sertifikasi"].set(peserta.sertifikasi)
        self.entries["skema"].set(peserta.skema)
        
        self.entries["nama"].delete(0, "end")
        self.entries["nama"].insert(0, peserta.nama)
        
        self.entries["nik"]._value = peserta.nik
        self.entries["nik"].delete(0, "end")
        self.entries["nik"].insert(0, self.entries["nik"]._format())
        
        self.entries["tempat_lahir"].delete(0, "end")
        self.entries["tempat_lahir"].insert(0, peserta.tempat_lahir)
        
        self.entries["tanggal_lahir"].delete(0, "end")
        self.entries["tanggal_lahir"].insert(0, peserta.tanggal_lahir)
        
        self.entries["alamat"].delete("1.0", "end")
        self.entries["alamat"].insert("1.0", peserta.alamat)
        
        self.entries["kelurahan"].delete(0, "end")
        self.entries["kelurahan"].insert(0, peserta.kelurahan)
        
        self.entries["kecamatan"].delete(0, "end")
        self.entries["kecamatan"].insert(0, peserta.kecamatan)
        
        self.entries["kabupaten"].delete(0, "end")
        self.entries["kabupaten"].insert(0, peserta.kabupaten)
        
        self.entries["provinsi"].delete(0, "end")
        self.entries["provinsi"].insert(0, peserta.provinsi)
        
        self.entries["telepon"].delete(0, "end")
        self.entries["telepon"].insert(0, peserta.telepon)
        
        self.entries["pendidikan"].set(peserta.pendidikan)
        
        self.entries["instansi"].delete(0, "end")
        self.entries["instansi"].insert(0, peserta.instansi)
    
    def next_peserta(self):
        """Pindah ke peserta selanjutnya"""
        # Validasi form saat ini
        peserta = self.collect_form()
        errors = peserta_validator.PesertaValidator.validate(peserta)
        if errors:
            for key, message in errors.items():
                self.entries[key].set_error(message)
            first_key = next(iter(errors))
            self.scroll_to_widget(self.entries[first_key])
            self.form_frame.focus_set()
            return
            
        
        # Update atau tambah ke list
        if self.current_index < len(self.list_peserta):
            self.list_peserta[self.current_index] = peserta
        else:
            self.list_peserta.append(peserta)
        
        # Show data container jika belum terlihat
        if len(self.list_peserta) > 0 and not self.data_container_wrapper.winfo_ismapped():
            self.data_container_wrapper.pack(fill="x", padx=50, pady=(0, 15), after=self.header_label)
        
        # Pindah ke index selanjutnya
        self.current_index += 1
        
        # Load data peserta berikutnya jika ada, atau reset form
        if self.current_index < len(self.list_peserta):
            self.load_form(self.list_peserta[self.current_index])
        else:
            self.clear_form()
                    
        # Update UI
        self.refresh_UI_Form()
    
    def _cek_form_filled(self):
        return (
                self.entries["nik"].get().strip() or
                self.entries["tempat_lahir"].get().strip() or
                self.entries["tanggal_lahir"].get().strip() or
                self.entries["alamat"].get().strip() or
                self.entries["kelurahan"].get().strip() or
                self.entries["kecamatan"].get().strip() or
                self.entries["kabupaten"].get().strip() or
                self.entries["provinsi"].get().strip() or
                self.entries["telepon"].get().strip() or
                self.entries["instansi"].get().strip()
            )
   
    def previous_peserta(self):
        """Kembali ke peserta sebelumnya"""
        if self.current_index > 0:
            # Simpan data saat ini jika ada isinya
            if self._cek_form_filled():
                peserta = self.collect_form()
                if self.current_index < len(self.list_peserta):
                    self.list_peserta[self.current_index] = peserta
                else:
                    self.list_peserta.append(peserta)
            
            # Pindah ke index sebelumnya
            self.current_index -= 1
            
            # Load data peserta sebelumnya
            self.load_form(self.list_peserta[self.current_index])
            
            # Update UI
            self.refresh_UI_Form()
       
    def clear_form(self):
        self.scroll_to_widget(self.header_label)
        self.form_frame.focus_set()
        for key, widget in self.entries.items():
            
            if key == "sertifikasi":
                continue
            
            if key == "skema":
                continue
            
            if key == "pendidikan":
                continue

            # 1. NikEntry
            if isinstance(widget, nik_entry.NikEntry):
                widget._value = ""
                widget.delete(0, "end")
                widget.insert(0, widget._format())

            # 2. ComboBox
            elif isinstance(widget, ctk.CTkComboBox):
                widget.set("")

            # 3. TextBox
            elif isinstance(widget, ctk.CTkTextbox):
                widget.delete("1.0", "end")

            # 4. Entry biasa
            else:
                try:
                    widget.delete(0, "end")
                except Exception:
                    pass
        
    
    def refresh_UI_Form(self):
        """Update label counter peserta"""
        self.counter_label.configure(text=f"Peserta #{self.current_index + 1}")
        
        """Update state tombol navigasi"""
        # Tombol prev hanya aktif jika bukan peserta pertama
        if self.current_index > 0:
            self.prev_btn.configure(state="normal")
        else:
            self.prev_btn.configure(state="disabled")
            
        # """Update state tombol navigasi"""
        # # Tombol prev hanya aktif jika bukan peserta pertama 
        # if self.current_index > 0:
        #     self.prev_btn.configure(state="normal")
        #     self.prev_btn.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        # else:
        #     self.prev_btn.grid_forget()
            
        """Update state sertifikasi combo box"""
        if len(self.list_peserta) >= 1:
            # Disable combo box, jadikan readonly
            self.entries["sertifikasi"].configure(state="disabled")
        else:
            # Enable combo box
            self.entries["sertifikasi"].configure(state="normal")
    
        """Update button data peserta di container"""
        # Hapus semua button lama
        for widget in self.data_scroll_frame.winfo_children():
            widget.destroy()
        
        # Buat button untuk setiap peserta
        row = 0
        col = 0
        for idx, peserta in enumerate(self.list_peserta):
            # Container untuk button + delete
            btn_container = ctk.CTkFrame(self.data_scroll_frame, fg_color="transparent")
            btn_container.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
            is_current = (idx == self.current_index)

            # Button data peserta
            btn = ctk.CTkButton(
                btn_container,
                text=f"#{idx + 1}",
                font=("Arial", 14, "bold"),
                fg_color="#1a73e8" if is_current else "#555555",
                hover_color="#1557b0" if is_current else "#666666",
                height=40,
                width=70,
                corner_radius=8,
                command=lambda i=idx: self.jump_to_peserta(i)
            )
            btn.pack(side="left", expand=True, fill="x")
            
            # Delete button
            del_btn = ctk.CTkButton(
                btn_container,
                text="✕",
                font=("Arial", 12, "bold"),
                fg_color="#dc3545",
                hover_color="#c82333",
                height=40,
                width=30,
                corner_radius=8,
                command=lambda i=idx: self.delete_peserta(i)
            )
            del_btn.pack(side="right", padx=(5, 0))
            
            # Update grid position
            col += 1
            if col >= 10:
                col = 0
                row += 1
    
    def jump_to_peserta(self, index):
        """Jump ke peserta tertentu"""
        # Simpan data saat ini dulu
        if self._cek_form_filled():
            peserta = self.collect_form()
            if self.current_index < len(self.list_peserta):
                self.list_peserta[self.current_index] = peserta
            else:
                # Form saat ini adalah peserta baru yang belum tersimpan
                self.list_peserta.append(peserta)
        
        # Pindah ke index yang dipilih
        self.current_index = index
        self.load_form(self.list_peserta[self.current_index])
        
        # Update UI
        self.refresh_UI_Form()
    
    def delete_peserta(self, index):
        """Hapus peserta tertentu"""
        if messagebox.askyesno("Konfirmasi", f"Hapus data peserta #{index + 1}?"):
            self.list_peserta.pop(index)
            
            # Adjust current index
            if self.current_index >= len(self.list_peserta):
                self.current_index = max(0, len(self.list_peserta) - 1)
            elif self.current_index > index:
                # Jika hapus peserta sebelum current, geser index
                self.current_index -= 1
                
            # Load data atau reset
            if len(self.list_peserta) > 0:
                if self.current_index < len(self.list_peserta):
                    # Load peserta yang ada
                    self.load_form(self.list_peserta[self.current_index])
                else:
                    # Current index di luar range, berarti form baru
                    self.clear_form()
            else:
                self.clear_form()
                self.current_index = 0
                # Hide data container
                self.data_container_wrapper.pack_forget()
            
            # Update UI
            self.refresh_UI_Form()
    
    def delete_all_data(self):
        """Hapus semua data peserta"""
        if len(self.list_peserta) == 0:
            messagebox.showinfo("Info", "Tidak ada data untuk dihapus")
            return
        
        if messagebox.askyesno("Konfirmasi", f"Hapus semua {len(self.list_peserta)} data peserta?"):
            self.list_peserta = []
            self.current_index = 0
            self.clear_form()
            
            # Hide data container
            self.data_container_wrapper.pack_forget()
            
            # Update UI
            self.refresh_UI_Form()
    
    def save_all_data(self):
        """Simpan semua data peserta"""
        # Validasi form saat ini terlebih dahulu
        peserta = self.collect_form()
        errors = peserta_validator.PesertaValidator.validate(peserta)
        if errors:
            for key, message in errors.items():
                self.entries[key].set_error(message)
            first_key = next(iter(errors))
            self.scroll_to_widget(self.entries[first_key])
            self.form_frame.focus_set()
            return
        
        # Simpan peserta terakhir
        if self.current_index < len(self.list_peserta):
            self.list_peserta[self.current_index] = peserta
        else:
            self.list_peserta.append(peserta)
        
        # Cek apakah ada peserta yang akan disimpan
        if len(self.list_peserta) == 0:
            messagebox.showwarning(
                "Peringatan",
                "Tidak ada data peserta untuk disimpan!"
            )
            return
        
        # Panggil fungsi simpan
        self.simpan_peserta(self.list_peserta)
        
        messagebox.showinfo(
            "Sukses",
            f"Berhasil menyimpan {len(self.list_peserta)} peserta!"
        )
        
        # Reset semua setelah simpan
        self.list_peserta = []
        self.current_index = 0
        self.clear_form()
        self.data_container_wrapper.pack_forget()
        self.refresh_UI_Form()
    
    def simpan_peserta(self, list_peserta):
        """
        Fungsi untuk menyimpan semua peserta
        Parameter: list_peserta (List[PesertaModel])
        """
        print("=" * 50)
        print("MENYIMPAN DATA PESERTA")
        print("=" * 50)
        
        for i, peserta in enumerate(list_peserta, start=1):
            print(f"\nPeserta #{i}:")
            print(f"  Sertifikasi: {peserta.sertifikasi}")
            print(f"  Skema: {peserta.skema}")
            print(f"  Nama: {peserta.nama}")
            print(f"  NIK: {peserta.nik}")
            print(f"  Tempat Lahir: {peserta.tempat_lahir}")
            print(f"  Tanggal Lahir: {peserta.tanggal_lahir}")
            print(f"  Alamat: {peserta.alamat}")
            print(f"  Kelurahan: {peserta.kelurahan}")
            print(f"  Kecamatan: {peserta.kecamatan}")
            print(f"  Kabupaten: {peserta.kabupaten}")
            print(f"  Provinsi: {peserta.provinsi}")
            print(f"  Telepon: {peserta.telepon}")
            print(f"  Pendidikan: {peserta.pendidikan}")
            print(f"  Instansi: {peserta.Instansi}")
        
        print("\n" + "=" * 50)
        print(f"Total: {len(list_peserta)} peserta")
        print("=" * 50)
        
        # TODO: Implementasi penyimpanan ke database atau file
        pass