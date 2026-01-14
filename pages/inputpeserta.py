import customtkinter as ctk
from tkinter import messagebox
import re, uuid
from models.peserta_model import PesertaModel
from services.database import (
    DB_Save_Peserta,
    DB_Get_All_Sertifikasi,
    DB_Get_Peserta_By_Id,
    DB_Get_Peserta_By_Sertifikasi,
    DB_Delete_Peserta_By_Sertifikasi)
from components import peserta_validator,create_entry,form_row,nik_entry
from config import PENDIDIKAN_OPTIONS,TEMPLATE_DOK_BNSP

class InputPesertaPage(ctk.CTkFrame):
    def __init__(self, parent, id_sertifikasi=None):
        super().__init__(parent, fg_color="#2a2a2a")

        self.sertifikasi = []
        self.sertifikasi_map = {}
        self.entries = {}
        self.error_labels = {}
        self.list_peserta = []
        self.placeholders = {}
        
        if id_sertifikasi:
            self.selected_id_sertifikasi = id_sertifikasi
        else:
            self.selected_id_sertifikasi = ""

        self.current_index = 0  
        
        self.DEFAULT_BORDER_COLOR = "#1a73e8"
        self.ERROR_BORDER_COLOR = "#ff4d4f"
        
        self.get_All_Sertifikasi()
        self._build_layout()
        self._build_container_data()
        self._build_form()
        
        
        if self.selected_id_sertifikasi:
            self._set_sertifikasi_by_id(self.selected_id_sertifikasi)
        else:
            self._update_selected_id()
        
        if self.selected_id_sertifikasi:
            self.load_peserta_from_sertifikasi()
        
        self.refresh_UI_Form()
    
    def _build_layout(self):
        self.main_container = ctk.CTkScrollableFrame(
            self, 
            fg_color="#2a2a2a",
            scrollbar_button_color="#888888",
            scrollbar_button_hover_color="#666666")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        self.main_container.bind_all("<MouseWheel>", self._on_mousewheel)
        self.main_container.bind("<Button-1>", lambda e: self.main_container.focus_set())

        self.header_label = ctk.CTkLabel(
            self.main_container,
            text="📝 INPUT DATA PESERTA",
            font=("Arial", 28, "bold"),
            text_color="#1a73e8"
        )
        self.header_label.pack(pady=(0, 10))
        self.header_label.bind("<Button-1>", lambda e: self.header_label.focus_set())

        self.form_container = ctk.CTkFrame(
            self.main_container,
            fg_color="#2a2a2a"
        )
        self.form_container.pack(fill="both", expand=True)
        self.form_container.bind("<Button-1>", lambda e: self.form_container.focus_set())

    def _build_container_data(self):
        self.data_container_wrapper = ctk.CTkFrame(self.main_container, fg_color="transparent")
        
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
        
        self.data_scroll_frame = ctk.CTkScrollableFrame(
            self.data_container_wrapper,
            fg_color="#333333",
            height=100,
            scrollbar_button_color="#888888",
            scrollbar_button_hover_color="#666666"
        )
        self.data_scroll_frame.pack(fill="x", pady=(0, 15))
        
        for i in range(10):  # 10 kolom
            self.data_scroll_frame.grid_columnconfigure(i, weight=1, minsize=100)
            
    # =======================
    # FORM
    # =======================
    def _build_form(self):
        self.form_frame = ctk.CTkFrame(self.form_container, fg_color="#333333", corner_radius=15)
        self.form_frame.pack(fill="both", expand=True, padx=50)
        self.form_frame.bind("<Button-1>", lambda e: self.form_frame.focus_set())

        
        # Form content dengan padding
        form_content = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        form_content.pack(fill="both", expand=True, padx=40, pady=40)
        form_content.bind("<Button-1>", lambda e: form_content.focus_set())

        # Header row dengan Sertifikasi dan Counter
        header_row = ctk.CTkFrame(form_content, fg_color="transparent")
        header_row.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        header_row.grid_columnconfigure(1, weight=1)
        header_row.bind("<Button-1>", lambda e: header_row.focus_set())

        # Sertifikasi combo box (kiri)
        sertifikasi_label = ctk.CTkLabel(header_row, text="Sertifikasi:", font=("Arial", 14, "bold"), text_color="#ffffff")
        sertifikasi_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        sertifikasi_label.bind("<Button-1>", lambda e: sertifikasi_label.focus_set())
        
        sertifikasi_options = self._generate_sertifikasi_options()
        
        entry = create_entry.createEntry(header_row, "combobox", options=sertifikasi_options, width=250)
        self.entries["sertifikasi"] = entry.widget
        self.entries["sertifikasi"].grid(row=0, column=1, sticky="w")
        self.entries["sertifikasi"].configure(state="readonly")
        
        # Set combo box berdasarkan id_sertifikasi yang dikirim
        if sertifikasi_options:
            if self.selected_id_sertifikasi:
                # Cari display text yang sesuai dengan ID
                self._set_sertifikasi_by_id(self.selected_id_sertifikasi)
            else:
                # Default ke option pertama
                self.entries["sertifikasi"].set(sertifikasi_options[0])
                self._update_selected_id()
                
        self.entries["sertifikasi"].configure(command=self._on_sertifikasi_change)
        self.entries["sertifikasi"].bind("<Button-1>", lambda e: self.entries["sertifikasi"].focus_set())

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
        self.counter_label.bind("<Button-1>", lambda e: self.counter_label.focus_set())

        # Row tracking
        current_row = 1
        
        # 1. Skema (ComboBox)
        entry = create_entry.createEntry(form_content, "combobox", options=["<Pilih Skema>"] + list(TEMPLATE_DOK_BNSP.keys()))
        self.entries["skema"] = entry.widget
        form_row.FormRow(form_content, current_row, "Skema", self.entries["skema"])
        current_row += 2
        
        # 2. Nama Lengkap
        self.placeholders["nama"] = "Masukkan nama lengkap"
        entry = create_entry.createEntry(form_content, "entry", placeholder=self.placeholders["nama"])
        self.entries["nama"] = entry.widget
        form_row.FormRow(form_content, current_row, "Nama Lengkap", self.entries["nama"])
        current_row += 2
        
        # 3. NIK (Custom dengan placeholder ─)   
        self.placeholders["nik"] = ""
        entry = create_entry.createEntry(form_content, "nik", placeholder=self.placeholders["nik"])
        self.entries["nik"] = entry.widget
        form_row.FormRow(form_content, current_row, "NIK", self.entries["nik"])
        current_row += 2
        
        # 4. Tempat Lahir
        self.placeholders["tempat_lahir"] = "Tempat lahir"
        entry = create_entry.createEntry(form_content, "entry", placeholder=self.placeholders["tempat_lahir"])
        self.entries["tempat_lahir"] = entry.widget
        form_row.FormRow(form_content, current_row, "Tempat Lahir", self.entries["tempat_lahir"])
        current_row += 2
        
        # 5. Tanggal Lahir 
        self.placeholders["tanggal_lahir"] = "DD-MM-YYYY"
        entry = create_entry.createEntry(form_content, "entry", placeholder=self.placeholders["tanggal_lahir"])
        self.entries["tanggal_lahir"] = entry.widget
        form_row.FormRow(form_content,current_row,"Tanggal Lahir",self.entries["tanggal_lahir"])
        self.entries["tanggal_lahir"].bind("<KeyPress>", self.format_tanggal_input)
        current_row += 2
        
        # 6. Alamat 
        self.placeholders["alamat"] = "Alamat lengkap"
        entry = create_entry.createEntry(form_content, "textbox", placeholder=self.placeholders["alamat"])
        self.entries["alamat"] = entry.widget
        form_row.FormRow(form_content, current_row, "Alamat", self.entries["alamat"])
        current_row += 2
        
        # 7. Kelurahan
        self.placeholders["kelurahan"] = "Nama kelurahan"
        entry = create_entry.createEntry(form_content, "entry", placeholder=self.placeholders["kelurahan"])
        self.entries["kelurahan"] = entry.widget
        form_row.FormRow(form_content, current_row, "Kelurahan", self.entries["kelurahan"])
        current_row += 2
        
        # 8. Kecamatan
        self.placeholders["kecamatan"] = "Nama kecamatan"
        entry = create_entry.createEntry(form_content, "entry", placeholder=self.placeholders["kecamatan"])
        self.entries["kecamatan"] = entry.widget
        form_row.FormRow(form_content, current_row, "Kecamatan", self.entries["kecamatan"])
        current_row += 2
        
        # 9. Kabupaten
        self.placeholders["kabupaten"] = "Nama kabupaten/kota"
        entry = create_entry.createEntry(form_content, "entry", placeholder=self.placeholders["kabupaten"])
        self.entries["kabupaten"] = entry.widget
        form_row.FormRow(form_content, current_row, "Kabupaten", self.entries["kabupaten"])
        current_row += 2
        
        # 10. Provinsi
        self.placeholders["provinsi"] = "Nama provinsi"
        entry = create_entry.createEntry(form_content,"entry", placeholder=self.placeholders["provinsi"])
        self.entries["provinsi"] = entry.widget
        form_row.FormRow(form_content, current_row, "Provinsi", self.entries["provinsi"])
        current_row += 2
        
        # 11. No. Telepon
        self.placeholders["telepon"] = "08xxxxxxxxxx"
        entry = create_entry.createEntry(form_content, "entry", placeholder=self.placeholders["telepon"])
        self.entries["telepon"] = entry.widget
        form_row.FormRow(form_content, current_row, "No. Telepon", self.entries["telepon"])
        self.entries["telepon"].bind("<KeyPress>", self.format_no_telepon)
        current_row += 2
        
        # 12. Pendidikan Terakhir
        entry = create_entry.createEntry(form_content, "combobox", options=["<Pilih Pendidikan>"] + PENDIDIKAN_OPTIONS)
        self.entries["pendidikan"] = entry.widget
        form_row.FormRow(form_content, current_row, "Pendidikan Terakhir", self.entries["pendidikan"])
        current_row += 2
        
        # 13. Instansi
        self.placeholders["instansi"] = "Nama Instansi"
        entry = create_entry.createEntry(form_content, "entry", placeholder=self.placeholders["instansi"])
        self.entries["instansi"] = entry.widget
        form_row.FormRow(form_content, current_row, "Instansi", self.entries["instansi"])
        current_row += 2
        
        for w in self.entries.values():
            w.bind("<FocusIn>", lambda e, widget=w: self.scroll_to_widget(widget))
        
        reset_frame = ctk.CTkFrame(form_content, fg_color="transparent")
        reset_frame.grid(row=current_row, column=0, columnspan=2, sticky="e", pady=(10, 20))
        
        self.reset_link = ctk.CTkLabel(
            reset_frame,
            text="🔄 Reset Form",
            font=("Arial", 13, "underline"),
            text_color="#ff051e",
            cursor="hand2"
        )
        self.reset_link.pack()
        self.reset_link.bind("<Button-1>", lambda e: self.clear_form())
        
        current_row += 1
        
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
        
        
        for i in range(3):
            button_frame.grid_columnconfigure(i, weight=1, uniform="buttons")

    # =======================
    # LOGIC
    # =======================
    def _set_sertifikasi_by_id(self, id_sertifikasi):
        """Set combo box berdasarkan ID yang dikirim"""
        for display_text, sert_id in self.sertifikasi_map.items():
            if sert_id == id_sertifikasi:
                self.entries["sertifikasi"].set(display_text)
                self.selected_id_sertifikasi = id_sertifikasi
                return
            
    def get_All_Sertifikasi(self):
        self.sertifikasi = DB_Get_All_Sertifikasi()
        
    def load_peserta_from_sertifikasi(self):
        if not self.selected_id_sertifikasi:
            return
        
        try:
            self.list_peserta = DB_Get_Peserta_By_Sertifikasi(self.selected_id_sertifikasi)
            
            if len(self.list_peserta) > 0:
                self.current_index = 0
                self.load_form(self.list_peserta[0])
            else:
                self.current_index = 0
                self.clear_form()
                
            print(f"[INFO] Loaded {len(self.list_peserta)} peserta from database")
            
        except Exception as e:
            print(f"[ERROR] Failed to load peserta: {e}")
            self.list_peserta = []
            self.current_index = 0
            
    def _compare_data_changes(self):
        original_list = DB_Get_Peserta_By_Sertifikasi(self.selected_id_sertifikasi)
        
        original_dict = {p.id_peserta: p for p in original_list}
        current_dict = {p.id_peserta: p for p in self.list_peserta}
        
        changes = {
            'modified': [],      
            'added': [],         
            'deleted': [],       
            'has_changes': False
        }
        
        for id_peserta, current_peserta in current_dict.items():
            if id_peserta in original_dict:
                original = original_dict[id_peserta]
                
                if (original.nama != current_peserta.nama or
                    original.nik != current_peserta.nik or
                    original.skema != current_peserta.skema or
                    original.tempat_lahir != current_peserta.tempat_lahir or
                    original.tanggal_lahir != current_peserta.tanggal_lahir or
                    original.alamat.strip() != current_peserta.alamat.strip() or
                    original.kelurahan != current_peserta.kelurahan or
                    original.kecamatan != current_peserta.kecamatan or
                    original.kabupaten != current_peserta.kabupaten or
                    original.provinsi != current_peserta.provinsi or
                    original.telepon != current_peserta.telepon or
                    original.pendidikan != current_peserta.pendidikan or
                    original.instansi != current_peserta.instansi):
                    
                    changes['modified'].append(current_peserta.nama)
                    changes['has_changes'] = True
            else:
                changes['added'].append(current_peserta.nama)
                changes['has_changes'] = True
                
        for id_peserta, original in original_dict.items():
            if id_peserta not in current_dict:
                changes['deleted'].append(original.nama)
                changes['has_changes'] = True
        
        return changes

    def _show_changes_dialog(self, changes):
        message_parts = []
        
        if changes['modified']:
            message_parts.append(f"✏️ DATA DIUBAH ({len(changes['modified'])}):")
            for nama in changes['modified'][:5]:  
                message_parts.append(f"  • {nama}")
            if len(changes['modified']) > 5:
                message_parts.append(f"  • ... dan {len(changes['modified']) - 5} lainnya")
            message_parts.append("")
        
        if changes['added']:
            message_parts.append(f"➕ DATA DITAMBAHKAN ({len(changes['added'])}):")
            for nama in changes['added'][:5]:
                message_parts.append(f"  • {nama}")
            if len(changes['added']) > 5:
                message_parts.append(f"  • ... dan {len(changes['added']) - 5} lainnya")
            message_parts.append("")
        
        if changes['deleted']:
            message_parts.append(f"🗑️ DATA DIHAPUS ({len(changes['deleted'])}):")
            for nama in changes['deleted'][:5]:
                message_parts.append(f"  • {nama}")
            if len(changes['deleted']) > 5:
                message_parts.append(f"  • ... dan {len(changes['deleted']) - 5} lainnya")
            message_parts.append("")
        
        message_parts.append("Simpan perubahan dan berganti sertifikasi?")
        
        message = "\n".join(message_parts)
        
        return messagebox.askyesno("Konfirmasi Perubahan", message)

    def _generate_sertifikasi_options(self):
        """Generate options untuk combo box dengan format: 'Sertifikasi Tanggal'"""
        options = []
        self.sertifikasi_map = {}
        
        for sert in self.sertifikasi:
            # Truncate nama sertifikasi jika lebih dari 20 karakter
            nama = sert["sertifikasi"]
            if len(nama) > 20:
                nama = nama[:17] + "..."
            
            # Format tanggal
            tanggal = sert["tanggal_pelatihan"]
            
            # Gabungkan jadi display text
            display_text = f"{nama} - {tanggal}"
            
            # Simpan mapping display_text -> id_sertifikasi
            self.sertifikasi_map[display_text] = sert["id_sertifikasi"]
            
            options.append(display_text)
        
        return options
    
    def _on_sertifikasi_change(self, choice):
        if len(self.list_peserta) > 0:
            try:
                peserta = self.collect_form()
                errors = peserta_validator.PesertaValidator.validate(peserta)
                
                if errors:
                    self._set_sertifikasi_by_id(self.selected_id_sertifikasi)
                    
                    for key, message in errors.items():
                        self.entries[key].set_error(message)
                    first_key = next(iter(errors))
                    self.scroll_to_widget(self.entries[first_key])
                    self.form_frame.focus_set()
                    
                    messagebox.showwarning(
                        "Validasi Gagal",
                        "Harap lengkapi data peserta sebelum berganti sertifikasi!"
                    )
                    return
                if self.current_index < len(self.list_peserta):
                    self.list_peserta[self.current_index] = peserta
                else:
                    self.list_peserta.append(peserta)
                
                changes = self._compare_data_changes()
                
                if changes['has_changes']:
                    if not self._show_changes_dialog(changes):
                        self._set_sertifikasi_by_id(self.selected_id_sertifikasi)
                        return
                    
                    self.simpan_peserta(self.list_peserta)
                    
                    messagebox.showinfo(
                        "Sukses",
                        f"Berhasil menyimpan perubahan!"
                    )
                
            except Exception as e:
                print(f"Gagal memproses data: {str(e)}")
                self._set_sertifikasi_by_id(self.selected_id_sertifikasi)
                return
        
        self._update_selected_id()
        self.load_peserta_from_sertifikasi()
        self.refresh_UI_Form()
    
    def _update_selected_id(self):
        current_text = self.entries["sertifikasi"].get()
        self.selected_id_sertifikasi = self.sertifikasi_map.get(current_text, "")
        print(f"[DEBUG] Selected ID: {self.selected_id_sertifikasi}")
        
    def format_tanggal_input(self, event):  
        entry = event.widget
        current_text = entry.get()
        
        navigation_keys = ["Left", "Right", "Home", "End", "Up", "Down"]
        if event.keysym in navigation_keys:
            return

        cursor_pos = entry.index("insert")
        
        current_digits = re.sub(r'\D', '', current_text)
        
        if event.keysym == "BackSpace":
            if cursor_pos > 0:
                separators_before = current_text[:cursor_pos].count('-')
                digit_pos = cursor_pos - separators_before - 1
                
                if digit_pos >= 0 and digit_pos < len(current_digits):
                    current_digits = current_digits[:digit_pos] + current_digits[digit_pos + 1:]
            else:
                return "break"
                
        elif event.char.isdigit():
            if len(current_digits) >= 8:
                return "break"
            
            separators_before = current_text[:cursor_pos].count('-')
            digit_pos = cursor_pos - separators_before
            
            current_digits = current_digits[:digit_pos] + event.char + current_digits[digit_pos:]
            
        else:
            return "break"
        
        formatted = ""
        for i, digit in enumerate(current_digits):
            if i == 2 or i == 4:
                formatted += "-"
            formatted += digit
        
        entry.delete(0, "end")
        entry.insert(0, formatted)
        
        if event.keysym == "BackSpace":
            new_cursor_pos = max(0, cursor_pos - 1)
            if new_cursor_pos > 0 and new_cursor_pos < len(formatted) and formatted[new_cursor_pos] == '-':
                new_cursor_pos -= 1
        else:
            new_digit_pos = digit_pos + 1
            
            if new_digit_pos > 4:
                new_cursor_pos = new_digit_pos + 2  
            elif new_digit_pos > 2:
                new_cursor_pos = new_digit_pos + 1  
            else:
                new_cursor_pos = new_digit_pos  
        
        entry.icursor(min(new_cursor_pos, len(formatted)))
        return "break"
    
    def format_no_telepon(self, event):
        if event.keysym == "BackSpace":
            return  
        elif event.char.isdigit():
            return 
        else:
            return "break"
        
    def _on_mousewheel(self, event):
        try:
            canvas = self.main_container._parent_canvas
            if not canvas.winfo_exists():
                return

            canvas.yview_scroll(
                int(-1 * (event.delta / 120)),
                "units"
            )
        except Exception:
            pass
        
    def scroll_to_widget(self, widget):
        try:
            widget.update_idletasks()
            self.main_container.update_idletasks()

            canvas = self.main_container._parent_canvas
            widget_y = widget.winfo_rooty() - self.form_frame.winfo_rooty()
            canvas_height = canvas.winfo_height()
            
            canvas.update_idletasks()
            bbox = canvas.bbox("all")
            if not bbox:
                return
            content_height = bbox[3] - bbox[1]
            
            if content_height <= canvas_height:
                return
            
            target_y = widget_y - 100
            
            scroll_position = target_y / content_height
            scroll_position = max(0.0, min(1.0, scroll_position))    
            canvas.yview_moveto(scroll_position)
            
        except Exception as e:
            print(f"Scroll error: {e}")
            pass

    def collect_form(self):
        while True:
            id_peserta = f"PSRT-{uuid.uuid4().hex[:8].upper()}"
            if not DB_Get_Peserta_By_Id(id_peserta):
                break
        if "<pilih pendidikan>" in self.entries["pendidikan"].get().strip().lower():
            pendidikan = ""
        else:
            pendidikan = self.entries["pendidikan"].get().upper()
            
        return PesertaModel(
            id_peserta=id_peserta,
            id_sertifikasi=self.selected_id_sertifikasi,
            skema=self.entries["skema"].get().upper(),
            nama=self.entries["nama"].get().upper(),
            nik=self.entries["nik"].get_value(),
            tempat_lahir=self.entries["tempat_lahir"].get().upper(),
            tanggal_lahir=self.entries["tanggal_lahir"].get(),
            alamat=self.entries["alamat"].get("1.0","end").strip().upper(),
            kelurahan=self.entries["kelurahan"].get().upper(),
            kecamatan=self.entries["kecamatan"].get().upper(),
            kabupaten=self.entries["kabupaten"].get().upper(),
            provinsi=self.entries["provinsi"].get().upper(),
            telepon=self.entries["telepon"].get(),
            pendidikan=pendidikan,
            instansi=self.entries["instansi"].get().upper()
        )
 
    def load_form(self, peserta: PesertaModel):
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
        if len(self.sertifikasi) <= 0:
            return
        peserta = self.collect_form()
        errors = peserta_validator.PesertaValidator.validate(peserta)
        if errors:
            for key, message in errors.items():
                self.entries[key].set_error(message)
            first_key = next(iter(errors))
            self.scroll_to_widget(self.entries[first_key])
            self.form_frame.focus_set()
            return
            
        if self.current_index < len(self.list_peserta):
            self.list_peserta[self.current_index] = peserta
        else:
            self.list_peserta.append(peserta)
        
        if len(self.list_peserta) > 0 and not self.data_container_wrapper.winfo_ismapped():
            self.data_container_wrapper.pack(fill="x", padx=50, pady=(0, 15), after=self.header_label)
        
        self.current_index += 1
        
        if self.current_index < len(self.list_peserta):
            self.load_form(self.list_peserta[self.current_index])
        else:
            self.clear_form()
                    
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
        if self.current_index > 0:
            if self._cek_form_filled():
                peserta = self.collect_form()
                if self.current_index < len(self.list_peserta):
                    self.list_peserta[self.current_index] = peserta
                else:
                    self.list_peserta.append(peserta)
            
            self.current_index -= 1
            self.load_form(self.list_peserta[self.current_index])
            self.refresh_UI_Form()
       
    def clear_form(self):
        self.scroll_to_widget(self.header_label)
        self.form_frame.focus_set()

        for key, widget in self.entries.items():

            if key == "sertifikasi":
                continue

            # =====================
            # 1. COMBOBOX
            # =====================
            if isinstance(widget, ctk.CTkComboBox):
                values = widget.cget("values")
                if len(values) > 1:
                    widget.set(values[0])
                else:
                    widget.set("")
                continue

            # =====================
            # 2. NIK ENTRY
            # =====================
            if isinstance(widget, nik_entry.NikEntry):
                widget._value = ""
                widget.delete(0, "end")
                widget.insert(0, widget._format())
                continue

            # =====================
            # 3. TEXTBOX
            # =====================
            if isinstance(widget, ctk.CTkTextbox):
                widget.delete("1.0", "end")

                placeholder = self.placeholders.get(key)
                if placeholder:
                    widget.insert("1.0", placeholder)
                continue

            # =====================
            # 4. ENTRY BIASA
            # =====================
            try:
                widget.delete(0, "end")

                placeholder = self.placeholders.get(key)
                if placeholder:
                    widget.insert(0, placeholder)

            except Exception:
                pass
         
    def refresh_UI_Form(self):
        self.counter_label.configure(text=f"Peserta #{self.current_index + 1}")
        
        if self.current_index > 0:
            self.prev_btn.configure(state="normal")
        else:
            self.prev_btn.configure(state="disabled")
            
        if self.current_index >= len(self.list_peserta):
            self.reset_link.configure(
                text_color="#ff051e",
                cursor="hand2"
            )
            self.reset_link.bind("<Button-1>", lambda e: self.clear_form())
        else:
            self.reset_link.configure(
                text_color="#666666", 
                cursor="arrow"  
            )
            self.reset_link.unbind("<Button-1>")
            
        if len(self.list_peserta) >= 1:
            if not self.data_container_wrapper.winfo_ismapped():
                self.data_container_wrapper.pack(fill="x", padx=50, pady=(0, 15), after=self.header_label)
        else:
            if self.data_container_wrapper.winfo_ismapped():
                self.data_container_wrapper.pack_forget()
    
        for widget in self.data_scroll_frame.winfo_children():
            widget.destroy()
        
        row = 0
        col = 0
        for idx, peserta in enumerate(self.list_peserta):
            btn_container = ctk.CTkFrame(self.data_scroll_frame, fg_color="transparent")
            btn_container.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
            is_current = (idx == self.current_index)

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
            
            col += 1
            if col >= 10:
                col = 0
                row += 1
    
    def jump_to_peserta(self, index):
        for key, w in self.entries.items():
            w.clear_error()
            
        if self._cek_form_filled():
            peserta = self.collect_form()
            if self.current_index < len(self.list_peserta):
                self.list_peserta[self.current_index] = peserta
            else:
                self.list_peserta.append(peserta)
        
        self.current_index = index
        self.load_form(self.list_peserta[self.current_index])
        self.refresh_UI_Form()
    
    def delete_peserta(self, index):
        if messagebox.askyesno("Konfirmasi", f"Hapus data peserta #{index + 1}?"):
            self.list_peserta.pop(index)
            
            if self.current_index >= len(self.list_peserta):
                self.current_index = max(0, len(self.list_peserta) - 1)
            elif self.current_index > index:
                self.current_index -= 1
                
            if len(self.list_peserta) > 0:
                if self.current_index < len(self.list_peserta):
                    self.load_form(self.list_peserta[self.current_index])
                else:
                    self.clear_form()
            else:
                self.clear_form()
                self.current_index = 0
                self.data_container_wrapper.pack_forget()
            
            self.refresh_UI_Form()
    
    def delete_all_data(self):
        if len(self.list_peserta) == 0:
            messagebox.showinfo("Info", "Tidak ada data untuk dihapus")
            return
        
        if messagebox.askyesno("Konfirmasi", f"Hapus semua {len(self.list_peserta)} data peserta?"):
            self.list_peserta = []
            self.current_index = 0
            self.clear_form()
            
            self.data_container_wrapper.pack_forget()
            self.refresh_UI_Form()
    
    def save_all_data(self):
        if len(self.sertifikasi) <= 0:
            return
            
        peserta = self.collect_form()
        errors = peserta_validator.PesertaValidator.validate(peserta)
        if errors:
            for key, message in errors.items():
                self.entries[key].set_error(message)
            first_key = next(iter(errors))
            self.scroll_to_widget(self.entries[first_key])
            self.form_frame.focus_set()
            return
        
        if self.current_index < len(self.list_peserta):
            self.list_peserta[self.current_index] = peserta
        else:
            self.list_peserta.append(peserta)
        
        if len(self.list_peserta) == 0:
            messagebox.showwarning(
                "Peringatan",
                "Tidak ada data peserta untuk disimpan!"
            )
            return
        
        try:
            changes = self._compare_data_changes()
            if changes['has_changes']:
                if not self._show_changes_dialog(changes):
                    return  
            else:
                messagebox.showinfo(
                    "Info",
                    "Tidak ada perubahan data untuk disimpan."
                )
                return
                
        except Exception as e:
            if not messagebox.askyesno(
                "Konfirmasi",
                f"Simpan {len(self.list_peserta)} peserta?"
            ):
                return
        
        try:
            self.simpan_peserta(self.list_peserta)
            
            messagebox.showinfo(
                "Sukses",
                f"Berhasil menyimpan {len(self.list_peserta)} peserta!"
            )
            
            self.load_peserta_from_sertifikasi()
            self.refresh_UI_Form()
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan data: {str(e)}")
    
    def simpan_peserta(self, list_peserta):
        try:            
            DB_Delete_Peserta_By_Sertifikasi(self.selected_id_sertifikasi)
            
            for i, peserta in enumerate(list_peserta, start=1):
                print(f"{i}. Saving Data {peserta.nama}")
                DB_Save_Peserta(peserta, self.selected_id_sertifikasi)
            
        except Exception as e:
            messagebox.showerror("Err",f"[ERROR] Gagal menyimpan peserta: {e}")
            raise e