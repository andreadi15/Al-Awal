# =======================
# FILE: pages/peserta.py
# =======================
import customtkinter as ctk
from tkinter import messagebox
from models.peserta_model import PesertaModel
from components.tambah_sertifikasi import AddSertifikasiDialog
from services.logic import return_format_tanggal,format_tempat_tanggal,format_alamat
from services.database import (
    DB_Get_All_Sertifikasi,
    DB_Get_Sertifikasi_By_ID,
    DB_Get_Peserta_By_Sertifikasi,
    DB_Delete_Sertifikasi,
    DB_Delete_Peserta_Batch,
    DB_Search_Peserta,
    DB_Search_Sertifikasi
)

class PesertaPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="#2a2a2a")
        self.bind("<Button-1>", lambda e: self.focus_set())
        
        self.app = app
        self.all_sertifikasi = []
        self.peserta_cache = {}
        
        self.selected_ids = {}
        self.expanded_sections = set()  
        self.search_text = ""
        self.date_filter = "Semua"  
        self.filtered_sertifikasi = []  
        
        self.rows_per_page = 10
        self.current_page = 1
        
        self.create_widgets()
        self.load_initial_data()
    
    def navigate_to_input_peserta(self, id_sertifikasi):
        self.app.show_page("Input Peserta", id_sertifikasi=id_sertifikasi)
        
    def load_initial_data(self):
        self.all_sertifikasi = DB_Get_All_Sertifikasi()
        self.update_date_filter_options() 
        self.refresh_display()
        
    def update_date_filter_options(self):
        if not self.all_sertifikasi:
            dates = ["Semua"]
        else:
            unique_dates = sorted(
                list(set([s['tanggal_pelatihan'] for s in self.all_sertifikasi])),
                reverse=True
            )
            dates = ["Semua"] + unique_dates
        
        self.date_combo.configure(values=dates)
        
        if self.date_filter not in dates:
            self.date_filter = "Semua"
            self.date_combo.set("Semua")

    def create_widgets(self):
        self.create_header()
        self.create_controls()
        self.create_tables_container()
    
    def create_header(self):
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent", height=80)
        self.header_frame.pack(fill="x", padx=20, pady=(20, 10))
        self.header_frame.pack_propagate(False)
        self.header_frame.bind("<Button-1>", lambda e: self.header_frame.focus_set())
        
        title = ctk.CTkLabel(
            self.header_frame,
            text="👥 Kelola Peserta",
            font=("Arial", 28, "bold"),
            text_color="#ffffff"
        )
        title.pack(side="left", pady=20)
        title.bind("<Button-1>", lambda e: title.focus_set())

        self.info_label = ctk.CTkLabel(
            self.header_frame,
            text="",
            font=("Arial", 14),
            text_color="#9e9e9e"
        )
        self.info_label.pack(side="left", padx=20)
        self.info_label.bind("<Button-1>", lambda e: self.info_label.focus_set())
    
    def create_controls(self):
        controls_frame = ctk.CTkFrame(self, fg_color="#1f1f1f", height=70)
        controls_frame.pack(fill="x", padx=20, pady=(0, 15))
        controls_frame.pack_propagate(False)
        controls_frame.bind("<Button-1>", lambda e: controls_frame.focus_set())
        
        search_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        search_frame.pack(side="left", padx=15, pady=10)

        ctk.CTkLabel(
            search_frame,
            text="Cari:",
            font=("Arial", 13)
        ).pack(side="left", padx=(0, 8))

        # Container untuk search entry + clear button
        search_container = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_container.pack(side="left")

        self.search_entry = ctk.CTkEntry(
            search_container,
            width=250,
            height=35,
            placeholder_text="Nama, NIK, Skema, Instansi..."
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<Return>", lambda e: self.apply_search())
        self.search_entry.bind("<KeyRelease>", lambda e: self.update_clear_button_visibility())

        # Clear button (inside search entry - hidden by default)
        self.clear_search_btn = ctk.CTkButton(
            search_container,
            text="✕",
            width=30,
            height=25,
            fg_color="transparent",
            hover_color="#ffebee",
            text_color="#d32f2f",
            font=("Arial", 16, "bold"),
            command=self.clear_search
        )
        # Position it inside the entry field on the right
        self.clear_search_btn.place(in_=self.search_entry, relx=0.92, rely=0.5, anchor="e")
        self.clear_search_btn.place_forget()  # Hide initially

        # Search button
        search_btn = ctk.CTkButton(
            search_frame,
            text="🔍",
            width=35,
            height=35,
            fg_color="#1a73e8",
            hover_color="#1557b0",
            font=("Arial", 19),
            command=self.apply_search
        )
        search_btn.pack(side="left", padx=5)
        
        date_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        date_frame.pack(side="left", padx=15, pady=10)
        
        ctk.CTkLabel(
            date_frame,
            text="📅 Tanggal:",
            font=("Arial", 13)
        ).pack(side="left", padx=(0, 8))
        
        self.date_combo = ctk.CTkComboBox(
            date_frame,
            values=["Semua"],
            width=150,
            height=35,
            command=lambda x: self.apply_date_filter(x)
        )
        self.date_combo.set("Semua")
        self.date_combo.configure(state="readonly")
        self.date_combo.pack(side="left")
                             
        refresh_btn = ctk.CTkButton(
            controls_frame,
            text="🔄 Refresh",
            width=100,
            height=40,
            font=("Arial", 14, "bold"),
            fg_color="#1557b0",
            hover_color="#1557b0",
            corner_radius=10,
            command=self.refresh_all
        )
        refresh_btn.pack(side="right", padx=15, pady=15)
        refresh_btn.bind("<Button-1>", lambda e: refresh_btn.focus_set())
        
        add_btn = ctk.CTkButton(
            controls_frame,
            text="➕ Tambah",
            width=100,
            height=40,
            font=("Arial", 14, "bold"),
            fg_color="#4caf50",
            hover_color="#45a049",
            corner_radius=10,
            command=self.show_add_sertifikasi_dialog
        )
        add_btn.pack(side="right", pady=15)     
    
    def create_tables_container(self):
        self.scroll_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.scroll_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def apply_date_filter(self, selected_value):
        self.date_filter = selected_value
        
        if selected_value == "Semua":
            self.filtered_sertifikasi = self.all_sertifikasi
        else:
            self.filtered_sertifikasi = [
                s for s in self.all_sertifikasi 
                if s['tanggal_pelatihan'] == selected_value
            ]
        
        self.refresh_display()
   
    def refresh_display(self):
        """Refresh display dengan data sertifikasi"""
        # Clear existing
        for widget in self.scroll_container.winfo_children():
            widget.destroy()
        
        # Determine display data - PERBAIKAN DI SINI
        if self.search_text:
            # Ada search active, pakai filtered results
            display_data = self.filtered_sertifikasi if self.filtered_sertifikasi is not None else []
        elif self.date_filter != "Semua":
            # Ada date filter, pakai filtered results
            display_data = self.filtered_sertifikasi if self.filtered_sertifikasi else []
        else:
            # Default: tampilkan semua
            display_data = self.all_sertifikasi
        
        # Update info
        total_sertifikasi = len(display_data)
        total_peserta = sum(s['jumlah_peserta'] for s in display_data)
        
        # Update info label based on state
        if self.search_text and display_data:
            # Search found results
            self.info_label.configure(
                text=f"🔍 {total_sertifikasi} Sertifikasi | {total_peserta} Peserta | '{self.search_text}'"
            )
        elif self.date_filter != "Semua" and display_data:
            # Date filter with results
            self.info_label.configure(
                text=f"📊 {total_sertifikasi} Sertifikasi | {total_peserta} Peserta | 📅 {self.date_filter}"
            )
        elif not display_data and (self.search_text or self.date_filter != "Semua"):
            # No results (handled in show_empty_state)
            pass  # Info label sudah diupdate di apply_search atau apply_date_filter
        else:
            # Default state
            self.info_label.configure(
                text=f"📊 {total_sertifikasi} Sertifikasi | {total_peserta} Total Peserta"
            )
        
        # Show content or empty state
        if not display_data:
            self.show_empty_state()
            return
        
        # Create sertifikasi sections
        for sertif in display_data:
            self.create_sertifikasi_section(sertif)
    
    def show_empty_state(self):
        """Show empty state with different messages"""
        empty_frame = ctk.CTkFrame(
            self.scroll_container,
            fg_color="#1f1f1f",
            height=250  # Tambah tinggi untuk button
        )
        empty_frame.pack(fill="x", pady=50)
        
        # Determine message based on state
        if self.search_text:
            icon = "🔍"
            message = f"Tidak ditemukan hasil untuk '{self.search_text}'"
            submessage = "Coba kata kunci lain atau periksa ejaan"
            color = "#ff9800"
            show_reset = True
        elif self.date_filter != "Semua":
            icon = "📅"
            message = f"Tidak ada sertifikasi pada tanggal {self.date_filter}"
            submessage = "Pilih tanggal lain atau tambah data baru"
            color = "#2196f3"
            show_reset = True
        else:
            icon = "📭"
            message = "Belum ada data sertifikasi"
            submessage = "Klik tombol 'Tambah' untuk membuat sertifikasi baru"
            color = "#666666"
            show_reset = False
        
        # Icon
        ctk.CTkLabel(
            empty_frame,
            text=icon,
            font=("Arial", 48)
        ).pack(pady=(40, 10))
        
        # Main message
        ctk.CTkLabel(
            empty_frame,
            text=message,
            font=("Arial", 18, "bold"),
            text_color=color
        ).pack(pady=(0, 5))
        
        # Submessage
        ctk.CTkLabel(
            empty_frame,
            text=submessage,
            font=("Arial", 12),
            text_color="#999999"
        ).pack(pady=(0, 20))
        
        # Reset button (only for search/filter)
        if show_reset:
            reset_btn = ctk.CTkButton(
                empty_frame,
                text="🔄 Reset Filter",
                width=150,
                height=35,
                fg_color="#1a73e8",
                hover_color="#1557b0",
                corner_radius=8,
                command=self.reset_all_filters
            )
            reset_btn.pack(pady=(0, 40))
        
    def reset_all_filters(self):
        """Reset semua filter (search dan date)"""
        # Clear search
        self.search_entry.delete(0, 'end')
        self.search_text = ""
        self.clear_search_btn.pack_forget()
        
        # Reset date filter
        self.date_filter = "Semua"
        self.date_combo.set("Semua")
        
        # Clear cache
        self.filtered_sertifikasi = []
        self.peserta_cache.clear()
        
        # Refresh display
        self.refresh_display()
        
    def create_sertifikasi_section(self, sertif):
        id_sertifikasi = sertif['id_sertifikasi']
        tanggal_pelatihan = return_format_tanggal(sertif['tanggal_pelatihan'])
        
        section_container = ctk.CTkFrame(
            self.scroll_container,
            fg_color="transparent"
        )
        section_container.pack(fill="x", pady=(0, 15))
        section_container.bind("<Button-1>", lambda e: section_container.focus_set())
        
        self.header_frame = ctk.CTkFrame(
            section_container,
            fg_color="#1a73e8",
            height=80,
            cursor="hand2"
        )
        self.header_frame.pack(fill="x")
        self.header_frame.pack_propagate(False)
        
        self.header_frame.bind(
            "<Button-1>",
            lambda e: (self.toggle_section(id_sertifikasi, section_container),section_container.focus_set())
        )
        
        left_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="y", padx=(15, 0))
        
        arrow_label = ctk.CTkLabel(
            left_frame,
            text="▶",
            font=("Arial", 18, "bold"),
            text_color="white",
            cursor="hand2"
        )
        arrow_label.pack(side="left", padx=(0, 10))
        arrow_label.bind(
            "<Button-1>",
            lambda e: (self.toggle_section(id_sertifikasi, section_container),section_container.focus_set())
        )
        
        nama_sertifikasi = sertif['sertifikasi']
        if len(nama_sertifikasi) > 35:
            display_nama = nama_sertifikasi[:32] + "..."
        else:
            display_nama = nama_sertifikasi
        
        name_label = ctk.CTkLabel(
            left_frame,
            text=f"📜 {display_nama}",
            font=("Arial", 16, "bold"),
            text_color="white",
            cursor="hand2"
        )
        name_label.pack(side="left")
        name_label.bind(
            "<Button-1>",
            lambda e: (self.toggle_section(id_sertifikasi, section_container),section_container.focus_set())
        )
        
        center_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        center_frame.pack(side="left", expand=True, padx=30)
        
        date_label = ctk.CTkLabel(
            center_frame,
            text=f"📅 {tanggal_pelatihan}",
            font=("Arial", 14, "bold"),
            text_color="white",
            cursor="hand2"
        )
        date_label.pack(side="left", padx=(0, 40))  
        date_label.bind(
            "<Button-1>",
            lambda e: (self.toggle_section(id_sertifikasi, section_container),section_container.focus_set())
        )
        
        count_label = ctk.CTkLabel(
            center_frame,
            text=f"👥 {sertif['jumlah_peserta']} peserta",
            font=("Arial", 14, "bold"),
            text_color="#ffeb3b",
            cursor="hand2"
        )
        count_label.pack(side="left")
        count_label.bind(
            "<Button-1>",
            lambda e: (self.toggle_section(id_sertifikasi, section_container),section_container.focus_set())
        )
        
        actions_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        actions_frame.pack(side="right", padx=10)
        
        add_peserta_btn = ctk.CTkButton(
            actions_frame,
            text="➕ Peserta",
            width=110,
            height=40,
            font=("Arial", 12, "bold"),
            fg_color="#0d4a9f",
            hover_color="#0a3a7f",
            corner_radius=8,
            command=lambda: self.navigate_to_input_peserta(id_sertifikasi)  
        )
        add_peserta_btn.pack(side="left", padx=3, pady=10)
        add_peserta_btn.bind("<Button-1>", lambda e: add_peserta_btn.focus_set())
        
        update_btn = ctk.CTkButton(
            actions_frame,
            text="✏️ Edit",
            width=90,
            height=40,
            font=("Arial", 12, "bold"),
            fg_color="#ff9800",
            hover_color="#f57c00",
            corner_radius=8,
            command=lambda: self.show_add_sertifikasi_dialog(sertif)
        )
        update_btn.pack(side="left", padx=3)
        update_btn.bind("<Button-1>", lambda e: update_btn.focus_set())
        
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️ Hapus",
            width=100,
            height=40,
            font=("Arial", 12, "bold"),
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            corner_radius=8,
            command=lambda: self.delete_sertifikasi(id_sertifikasi)
        )
        delete_btn.pack(side="left", padx=3)
        delete_btn.bind("<Button-1>", lambda e: delete_btn.focus_set())
        
        menu_btn = ctk.CTkButton(
            actions_frame,
            text="⋮",
            width=50,
            height=40,
            font=("Arial", 20, "bold"),
            fg_color="#555555",
            hover_color="#444444",
            corner_radius=8,
            command=lambda: self.show_menu_dropdown(id_sertifikasi, tanggal_pelatihan, menu_btn)
        )
        menu_btn.pack(side="left", padx=3)
        menu_btn.bind("<Button-1>", lambda e: menu_btn.focus_set())
        
        content_frame = ctk.CTkFrame(section_container, fg_color="#1f1f1f")
        
        section_container._id_sertifikasi = id_sertifikasi
        section_container._content_frame = content_frame
        section_container._arrow_label = arrow_label
        section_container._is_expanded = False
        
    def toggle_section(self, id_sertifikasi, container):
        is_expanded = container._is_expanded
        
        if is_expanded:
            container._content_frame.pack_forget()
            container._arrow_label.configure(text="▶")
            container._is_expanded = False
            self.expanded_sections.discard(id_sertifikasi)
        else:
            if id_sertifikasi not in self.peserta_cache:
                self.load_peserta_for_sertifikasi(id_sertifikasi)
            
            self.render_peserta_table(container._content_frame, id_sertifikasi)
            
            container._content_frame.pack(fill="x", pady=(2, 0))
            container._arrow_label.configure(text="▼")
            container._is_expanded = True
            self.expanded_sections.add(id_sertifikasi)
    
    def load_peserta_for_sertifikasi(self, id_sertifikasi):
        try:
            peserta_list = DB_Get_Peserta_By_Sertifikasi(id_sertifikasi)
            self.peserta_cache[id_sertifikasi] = peserta_list
            
            print(f"✓ Loaded {len(peserta_list)} peserta for {id_sertifikasi}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal load peserta: {str(e)}")
            self.peserta_cache[id_sertifikasi] = []
            
    def render_peserta_table(self, content_frame, id_sertifikasi):
        for widget in content_frame.winfo_children():
            widget.destroy()
        
        peserta_list = self.peserta_cache.get(id_sertifikasi, [])
        
        if not peserta_list:
            empty_label = ctk.CTkLabel(
                content_frame,
                text="📭 Tidak ada peserta",
                font=("Arial", 14),
                text_color="#666666"
            )
            empty_label.pack(pady=30)
            return
        
        self.create_action_panel(content_frame, id_sertifikasi)
        
        self.create_table_headers(content_frame)
        
        for index,peserta in enumerate(peserta_list,start=1):
            self.create_table_row(content_frame, index, peserta, id_sertifikasi)  
    
    def create_action_panel(self, parent, id_sertifikasi):
        panel = ctk.CTkFrame(parent, fg_color="#d32f2f", height=50, corner_radius=10)
        panel.pack(fill="x", padx=10, pady=10)
        panel.pack_propagate(False)
        
        delete_btn = ctk.CTkButton(
            panel,
            text="🗑️ Hapus Terpilih",
            width=140,
            height=35,
            fg_color="#b71c1c",
            hover_color="#8b0000",
            corner_radius=8,
            command=lambda: self.delete_selected(id_sertifikasi)
        )
        delete_btn.pack(side="left", padx=15)
        
        count = len(self.selected_ids.get(id_sertifikasi, set()))
        count_label = ctk.CTkLabel(
            panel,
            text=f"Terpilih: {count} item",
            font=("Arial", 13, "bold"),
            text_color="white"
        )
        count_label.pack(side="left", padx=10)
        
        parent._action_panel = panel
        parent._count_label = count_label
    
    def create_table_headers(self, parent):
        self.header_frame = ctk.CTkFrame(parent, fg_color="#333333", height=45)
        self.header_frame.pack(fill="x", padx=10, pady=(0, 2))
        self.header_frame.pack_propagate(False)
        
        self.header_frame.grid_columnconfigure(0, weight=0, minsize=65)   
        self.header_frame.grid_columnconfigure(1, weight=0, minsize=50)   
        self.header_frame.grid_columnconfigure(2, weight=0, minsize=180)  
        self.header_frame.grid_columnconfigure(3, weight=0, minsize=150)  
        self.header_frame.grid_columnconfigure(4, weight=0, minsize=180)  
        self.header_frame.grid_columnconfigure(5, weight=0, minsize=160)  
        self.header_frame.grid_columnconfigure(6, weight=0, minsize=190)  
        self.header_frame.grid_columnconfigure(7, weight=0, minsize=270)  
        self.header_frame.grid_columnconfigure(8, weight=0, minsize=125)  
        self.header_frame.grid_columnconfigure(9, weight=0, minsize=100)  
        
        headers = [
            ("   ☑", 0),
            ("No", 1),
            ("Nama Peserta", 2),
            ("Instansi", 3),
            ("Skema", 4),
            ("NIK", 5),
            ("Tempat/Tgl Lahir", 6),
            ("Alamat", 7),
            ("No HP", 8),
            ("Pendidikan", 9)
        ]
        
        for header_text, col_index in headers:
            label = ctk.CTkLabel(
                self.header_frame,
                text=header_text,
                font=("Arial", 13, "bold"),
                text_color="#ffffff",
                anchor="w"
            )
            label.grid(row=0, column=col_index, padx=5, sticky="w")
            
    def create_table_row(self, parent, index, peserta: PesertaModel, id_sertifikasi):
        row_frame = ctk.CTkFrame(parent, fg_color="#2a2a2a")
        row_frame.pack(fill="x", padx=10, pady=1)
        
        row_frame.grid_columnconfigure(0, weight=0, minsize=50)
        row_frame.grid_columnconfigure(1, weight=0, minsize=50)
        row_frame.grid_columnconfigure(2, weight=0, minsize=180)
        row_frame.grid_columnconfigure(3, weight=0, minsize=150)
        row_frame.grid_columnconfigure(4, weight=0, minsize=180)
        row_frame.grid_columnconfigure(5, weight=0, minsize=160)
        row_frame.grid_columnconfigure(6, weight=0, minsize=190)
        row_frame.grid_columnconfigure(7, weight=0, minsize=270)
        row_frame.grid_columnconfigure(8, weight=0, minsize=125)
        row_frame.grid_columnconfigure(9, weight=0, minsize=100)
        
        peserta_id = peserta.id_peserta
        check_var = ctk.BooleanVar(value=peserta_id in self.selected_ids.get(id_sertifikasi, set()))
        checkbox = ctk.CTkCheckBox(
            row_frame,
            text="",
            width=30,
            variable=check_var,
            command=lambda: self.toggle_selection(peserta_id, check_var, id_sertifikasi)
        )
        checkbox.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        cells_config = [
            (str(index), 1, 12, 0),
            (peserta.nama, 2, 12, 135),        
            (peserta.instansi, 3, 12, 105),    
            (peserta.skema, 4, 12, 135),       
            (peserta.nik[:16] if peserta.nik else "", 5, 12, 0),
            (format_tempat_tanggal(peserta.tempat_lahir, peserta.tanggal_lahir),6, 12, 145),  
            (format_alamat(peserta), 7, 12, 205), 
            (peserta.telepon, 8, 12, 0),
            (peserta.pendidikan, 9, 12, 70),   
        ]

        
        for cell_text, col_index, font_size, wrap_length in cells_config:
            display_text = str(cell_text) if cell_text else ""
            
            label = ctk.CTkLabel(
                row_frame,
                text=display_text,
                font=("Arial", font_size),
                text_color="#ffffff",
                anchor="nw",  
                justify="left",
                wraplength=wrap_length 
            )
            label.grid(row=0, column=col_index, padx=5, pady=5, sticky="nw")
            
    def toggle_selection(self, peserta_id, var, id_sertifikasi):
        for other_id in list(self.selected_ids.keys()):
            if other_id != id_sertifikasi and self.selected_ids[other_id]:
                self.selected_ids[other_id].clear()
                self.update_action_panel(other_id)
                
        if id_sertifikasi not in self.selected_ids:
            self.selected_ids[id_sertifikasi] = set()
        
        if var.get():
            self.selected_ids[id_sertifikasi].add(peserta_id) 
        else:
            self.selected_ids[id_sertifikasi].discard(peserta_id)
        
        self.update_action_panel(id_sertifikasi)
    
    def update_action_panel(self, id_sertifikasi):
        for widget in self.scroll_container.winfo_children():
            if (hasattr(widget, '_id_sertifikasi') and 
                widget._id_sertifikasi == id_sertifikasi):
                content = widget._content_frame
                if hasattr(content, '_count_label'):
                    count = len(self.selected_ids.get(id_sertifikasi, set()))
                    content._count_label.configure(
                        text=f"Terpilih: {count} item"
                    )
                break
    
    def delete_selected(self, id_sertifikasi):
        selected_in_this_sertifikasi = self.selected_ids.get(id_sertifikasi, set())
        
        if not self.selected_ids:
            messagebox.showinfo("Info", "Tidak ada item yang dipilih!")
            return
        
        result = messagebox.askyesno(
            "Konfirmasi",
            f"Hapus {len(selected_in_this_sertifikasi)} peserta terpilih?\n\nData tidak dapat dikembalikan!"
        )
        
        if result:
            try:
                peserta_list = self.peserta_cache.get(id_sertifikasi, [])
                id_peserta_list = [
                    p.id_peserta for p in peserta_list 
                    if p.id_peserta in selected_in_this_sertifikasi
                ]
                
                deleted = DB_Delete_Peserta_Batch(id_peserta_list)
                
                if deleted > 0:
                    self.peserta_cache[id_sertifikasi] = [
                        p for p in peserta_list 
                        if p.id_peserta not in self.selected_ids
                    ]
                    
                    self.selected_ids.clear()
                    self.refresh_all()
                    
                    messagebox.showinfo("Sukses", f"{deleted} peserta berhasil dihapus!")
                else:
                    messagebox.showwarning("Warning", "Tidak ada data yang dihapus")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menghapus data: {str(e)}")
    
    # INI BARU
    def apply_search(self):
        """Apply search filter"""
        search_text = self.search_entry.get().strip()
        
        # Update clear button visibility
        self.update_clear_button_visibility()
        
        # Clear search - jika input kosong
        if not search_text:
            self.search_text = ""
            self.filtered_sertifikasi = []
            self.peserta_cache.clear()
            self.clear_search_btn.place_forget()
            self.refresh_display()
            return
        
        # Already searching same text - skip
        if search_text == self.search_text:
            return
        
        # Update search text
        self.search_text = search_text
        
        # Show loading indicator
        self.info_label.configure(text="🔍 Mencari...")
        self.update_idletasks()
        
        try:
            # Search sertifikasi by name
            filtered_sertifikasi = DB_Search_Sertifikasi(self.search_text)
            
            # Search peserta and group by sertifikasi
            peserta_results = DB_Search_Peserta(self.search_text)
            
            # Combine results
            combined_sertifikasi_ids = set()
            
            # Add sertifikasi that match by name
            for sertif in filtered_sertifikasi:
                combined_sertifikasi_ids.add(sertif['id_sertifikasi'])
            
            # Add sertifikasi that have matching peserta
            for id_sertifikasi in peserta_results.keys():
                combined_sertifikasi_ids.add(id_sertifikasi)
            
            # Get full sertifikasi data for all matches
            if combined_sertifikasi_ids:
                # Apply date filter if active
                if self.date_filter == "Semua":
                    base_data = self.all_sertifikasi
                else:
                    base_data = [s for s in self.all_sertifikasi if s['tanggal_pelatihan'] == self.date_filter]
                
                # Filter to only matching sertifikasi
                self.filtered_sertifikasi = [
                    s for s in base_data 
                    if s['id_sertifikasi'] in combined_sertifikasi_ids
                ]
                
                # Cache filtered peserta results
                for id_sertifikasi, peserta_list in peserta_results.items():
                    self.peserta_cache[id_sertifikasi] = peserta_list
                
                # Refresh display
                self.refresh_display()
                
                # Update info label - HASIL DITEMUKAN
                total_peserta = sum(len(peserta_results.get(s['id_sertifikasi'], [])) for s in self.filtered_sertifikasi)
                self.info_label.configure(
                    text=f"🔍 {len(self.filtered_sertifikasi)} Sertifikasi | {total_peserta} Peserta | '{self.search_text}'"
                )
            else:
                # No results found - SET FILTERED KE EMPTY LIST
                self.filtered_sertifikasi = []
                self.peserta_cache.clear()
                
                # Refresh display - INI AKAN TRIGGER show_empty_state
                self.refresh_display()
                
                # Update info label - TIDAK DITEMUKAN
                self.info_label.configure(
                    text=f"🔍 '{self.search_text}' - Tidak ada hasil"
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mencari: {str(e)}")
            self.info_label.configure(text="❌ Error saat mencari")
   
    # INI BARU 
    def clear_search(self):
        """Clear search and reset display"""
        self.search_entry.delete(0, 'end')
        self.search_text = ""
        self.after(10, lambda: self.header_frame.focus_set())
        
        # Hide clear button
        self.clear_search_btn.place_forget()        
        
        self.filtered_sertifikasi = []
        self.peserta_cache.clear()
        
        self.refresh_display()
    
    def update_clear_button_visibility(self):
        """Show/hide clear button based on search entry content"""
        if self.search_entry.get().strip():
            # Show clear button
            self.clear_search_btn.place(in_=self.search_entry, relx=0.86, rely=0.5, anchor="w")
        else:
            # Hide clear button
            self.clear_search_btn.place_forget()
            
    def refresh_all(self):
        self.peserta_cache.clear()
        self.selected_ids.clear()
        expanded_before = self.expanded_sections.copy()
        self.expanded_sections.clear()
        
        self.all_sertifikasi = DB_Get_All_Sertifikasi()
        self.update_date_filter_options()
        self.refresh_display()
        
        for id_sertifikasi in expanded_before:
            for widget in self.scroll_container.winfo_children():
                if (hasattr(widget, '_id_sertifikasi') and 
                    widget._id_sertifikasi == id_sertifikasi):
                    self.toggle_section(id_sertifikasi, widget)
                    break
                
    def show_add_sertifikasi_dialog(self, sertif=None):
        if sertif == None:
            AddSertifikasiDialog(self, self.on_sertifikasi_added)
        else:
            AddSertifikasiDialog(self, self.on_sertifikasi_added, sertif)
    
    def on_sertifikasi_added(self):
        self.refresh_all()
        
    def delete_sertifikasi(self, id_sertifikasi):
        if messagebox.askyesno("Konfirmasi", f"Konfirmasi Untuk Hapus?"):
            DB_Delete_Sertifikasi(id_sertifikasi,True)
            self.refresh_all()
         
    def show_import_dialog(self,id_sertifikasi):
        from components.import_dialog import ImportDialog
        ImportDialog(self, self.refresh_all, id_sertifikasi)    
        
    def show_menu_dropdown(self, id_sertifikasi, tanggal_pelatihan, button):
        menu = ctk.CTkToplevel(self)
        menu.title("")
        menu.overrideredirect(True)  
        menu.configure(fg_color="#1f1f1f")
        
        menu_width = 150
        x = button.winfo_rootx() - menu_width + button.winfo_width() -40 
        y = button.winfo_rooty() + button.winfo_height()
        menu.geometry(f"{menu_width}x120+{x}+{y}")
        
        menu.attributes('-topmost', True)
        menu.transient(self)
        
        ctk.CTkButton(
            menu,
            text="📋 Salin",
            width=160,
            height=35,
            fg_color="transparent",
            hover_color="#333333",
            anchor="w",
            font=("Arial", 13),
            command=lambda: (menu.destroy(), self.copy_peserta_data(id_sertifikasi))
        ).pack(pady=2, padx=10)
        
        ctk.CTkButton(
            menu,
            text="📥 Import",
            width=160,
            height=35,
            fg_color="transparent",
            hover_color="#333333",
            anchor="w",
            font=("Arial", 13),
            command=lambda: (menu.destroy(), self.show_import_dialog(id_sertifikasi))
        ).pack(pady=2, padx=10)
        
        ctk.CTkButton(
            menu,
            text="📤 Ekspor",
            width=160,
            height=35,
            fg_color="transparent",
            hover_color="#333333",
            anchor="w",
            font=("Arial", 13),
            command=lambda: (menu.destroy(), self.show_export_dialog(id_sertifikasi, tanggal_pelatihan))
        ).pack(pady=2, padx=10)                
        
        def close_menu(event):
            if event.widget != menu:
                menu.destroy()
        
        self.after(100, lambda: menu.bind_all("<Button-1>", close_menu, add="+"))

    def show_export_dialog(self, id_sertifikasi, tanggal_pelatihan):
        peserta_list = DB_Get_Peserta_By_Sertifikasi(id_sertifikasi)
        
        if not peserta_list:
            messagebox.showinfo("Info", "Tidak ada peserta untuk diekspor!")
            return
        
        sertifikasi_info = {
            'id_sertifikasi': id_sertifikasi,
            'tanggal_pelatihan': tanggal_pelatihan
        }
        
        from components.export_dialog import ExportDialog
        ExportDialog(self, peserta_list, sertifikasi_info, self.refresh_all)

    def copy_peserta_data(self, id_sertifikasi):
        sertif = DB_Get_Sertifikasi_By_ID(id_sertifikasi)
        if not sertif:
            messagebox.showerror("Error", "Sertifikasi tidak ditemukan!")
            return
        
        peserta_list = DB_Get_Peserta_By_Sertifikasi(id_sertifikasi)
        
        if not peserta_list:
            messagebox.showinfo("Info", "Tidak ada peserta untuk disalin!")
            return
        
        def wrap(val):
            return f"⟦{str(val).replace('⟦','').replace('⟧','')}⟧"

        lines = []
        for i, p in enumerate(peserta_list, start=1):
            line = "".join([
                wrap(i),
                wrap(p.nama),
                wrap(p.skema),
                wrap(p.nik),
                wrap(p.tempat_lahir),
                wrap(p.tanggal_lahir),
                wrap(p.alamat),
                wrap(p.kelurahan),
                wrap(p.kecamatan),
                wrap(p.kabupaten),
                wrap(p.provinsi),
                wrap(p.telepon),
                wrap(p.pendidikan),
                wrap(p.instansi),
            ])
            lines.append(line)

        header = "".join([
            wrap("AWL-Copy"),
            wrap(sertif["sertifikasi"]),
            wrap(sertif["tanggal_pelatihan"]),
        ])

        result_text = header + "\n" + "\n".join(lines)

        self.clipboard_clear()
        self.clipboard_append(result_text)
        
        messagebox.showinfo(
            f"✅ {len(peserta_list)} peserta berhasil disalin!"
        )
        
        