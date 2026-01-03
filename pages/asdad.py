# =======================
# FILE: main.py (PERUBAHAN)
# =======================

class App(ctk.CTk):
    # ... kode lainnya tidak berubah ...
    
    def __init__(self):
        super().__init__()
        # ... kode lainnya ...
        
        self.id_sertifikasi = ""
        self.nav_visible = True
        self.current_page = None
        self.current_page_name = None  # Track nama halaman saat ini
        
        # ... kode lainnya ...

    def show_page(self, page_name, id_sertifikasi=None):
        """
        Ganti halaman yang ditampilkan dengan optional id_sertifikasi
        
        Args:
            page_name: Nama halaman yang akan ditampilkan
            id_sertifikasi: Optional ID sertifikasi untuk dikirim ke halaman
        """
        # Destroy current page
        if self.current_page:
            for widget in self.content_container.winfo_children():
                widget.destroy()
        
        # Update id_sertifikasi jika diberikan
        if id_sertifikasi is not None:
            self.id_sertifikasi = id_sertifikasi
        
        # Update menu highlights
        for name, btn in self.menu_buttons.items():
            if name == page_name:
                btn.configure(fg_color="#B8B8B8", text_color="#333333")
            else:
                if not getattr(btn, '_is_hovered', False):
                    btn.configure(fg_color="transparent", text_color="#ffffff")
        
        # Load new page dengan id_sertifikasi
        if page_name == "Dashboard":
            page = DashboardPage(self.content_container)
        elif page_name == "Peserta":
            page = PesertaPage(self.content_container, self)  # Pass app reference
        elif page_name == "Input Peserta":
            page = InputPesertaPage(self.content_container, self.id_sertifikasi)
        elif page_name == "Projects":
            page = ProjectsPage(self.content_container)
        elif page_name == "Settings":
            page = SettingsPage(self.content_container)
        else:
            page = DashboardPage(self.content_container)
        
        page.pack(fill="both", expand=True)
        self.current_page = page
        self.current_page_name = page_name


# =======================
# FILE: pages/peserta.py (PERUBAHAN)
# =======================

class PesertaPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="#2a2a2a")
        
        self.app = app  # Store reference ke App
        
        # ... kode lainnya tidak berubah ...
        
    def create_sertifikasi_section(self, sertif):
        """Create collapsible section untuk satu sertifikasi"""
        id_sertifikasi = sertif['id_sertifikasi']
        
        # ... kode lainnya tidak berubah sampai Action Buttons ...
        
        # Action Buttons Frame - Column 4
        actions_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=4, padx=10, sticky="e")
        
        # Add Peserta Button - UBAH COMMAND INI
        add_peserta_btn = ctk.CTkButton(
            actions_frame,
            text="➕ Peserta",
            width=110,
            height=32,
            font=("Arial", 11, "bold"),
            fg_color="#4caf50",
            hover_color="#45a049",
            corner_radius=6,
            command=lambda: self.navigate_to_input_peserta(id_sertifikasi)
        )
        add_peserta_btn.pack(side="left", padx=3, pady=10)
        
        # ... button lainnya tidak berubah ...
    
    def navigate_to_input_peserta(self, id_sertifikasi):
        """Navigate ke halaman Input Peserta dengan ID sertifikasi"""
        self.app.show_page("Input Peserta", id_sertifikasi=id_sertifikasi)


# =======================
# FILE: pages/inputpeserta.py (PERUBAHAN)
# =======================

class InputPesertaPage(ctk.CTkFrame):
    def __init__(self, parent, id_sertifikasi=None):
        super().__init__(parent, fg_color="#2a2a2a")

        self.sertifikasi = []
        self.sertifikasi_map = {}
        self.entries = {}
        self.error_labels = {}
        self.list_peserta = []
        
        # Set ID sertifikasi
        if id_sertifikasi:
            self.selected_id_sertifikasi = id_sertifikasi
        else:
            self.selected_id_sertifikasi = ""
        
        # ... kode lainnya tidak berubah sampai _build_form ...
    
    def _build_form(self):
        # ... kode lainnya tidak berubah sampai combo box sertifikasi ...
        
        # Generate options
        sertifikasi_options = self._generate_sertifikasi_options()
        
        entry = create_entry.createEntry(header_row, "combobox", options=sertifikasi_options, width=250)
        self.entries["sertifikasi"] = entry.widget
        self.entries["sertifikasi"].grid(row=0, column=1, sticky="w")
        
        # Set combo box berdasarkan id_sertifikasi yang dikirim
        if sertifikasi_options:
            if self.selected_id_sertifikasi:
                # Cari display text yang sesuai dengan ID
                self._set_sertifikasi_by_id(self.selected_id_sertifikasi)
            else:
                # Default ke option pertama
                self.entries["sertifikasi"].set(sertifikasi_options[0])
                self._update_selected_id()
        
        # Bind event
        self.entries["sertifikasi"].configure(command=self._on_sertifikasi_change)
        self.entries["sertifikasi"].bind("<Button-1>", lambda e: self.entries["sertifikasi"].focus_set())
        
        # ... kode lainnya tidak berubah ...
    
    def _set_sertifikasi_by_id(self, id_sertifikasi):
        """Set combo box berdasarkan ID sertifikasi"""
        # Cari display text yang sesuai dengan ID
        for display_text, sert_id in self.sertifikasi_map.items():
            if sert_id == id_sertifikasi:
                self.entries["sertifikasi"].set(display_text)
                self.selected_id_sertifikasi = id_sertifikasi
                print(f"[DEBUG] Sertifikasi diset ke: {display_text} (ID: {id_sertifikasi})")
                return
        
        # Jika tidak ditemukan, set ke default
        if self.sertifikasi_map:
            first_option = list(self.sertifikasi_map.keys())[0]
            self.entries["sertifikasi"].set(first_option)
            self._update_selected_id()
            print(f"[WARNING] ID {id_sertifikasi} tidak ditemukan, menggunakan default")


# =======================
# CONTOH PENGGUNAAN
# =======================

# Dari PesertaPage, tombol "➕ Peserta" akan:
# 1. Ambil id_sertifikasi dari section
# 2. Panggil self.app.show_page("Input Peserta", id_sertifikasi="CERT123")
# 3. InputPesertaPage akan langsung menampilkan sertifikasi yang dipilih