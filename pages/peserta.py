# =======================
# FILE: pages/peserta.py
# =======================
import customtkinter as ctk
from tkinter import messagebox
import os
from datetime import datetime, timedelta
from pages.peserta_model import PesertaModel
from pages.tambah_sertifikasi import AddSertifikasiDialog
from services.export_awl_report import exportExcel
from services.logic import return_format_tanggal
from services.database import (
    DB_Get_All_Sertifikasi,
    DB_Get_Peserta_By_Sertifikasi,
    DB_Delete_Sertifikasi,
    DB_Delete_Peserta_Batch,
    DB_Search_Peserta
)

class PesertaPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="#2a2a2a")
        self.bind("<Button-1>", lambda e: self.focus_set())
        
        self.app = app
        # Data dummy
        self.all_sertifikasi = []
        self.peserta_cache = {}
        
        # State management
        self.selected_ids = {}
        self.expanded_sections = set()  # Track yang sudah di-expand
        self.search_text = ""
        self.date_filter = "Semua"  # Track filter tanggal
        self.filtered_sertifikasi = []  # Data sertifikasi yang sudah difilter
        
        # Settings
        self.rows_per_page = 10
        self.current_page = 1
        
        self.create_widgets()
        self.load_initial_data()
    
    def navigate_to_input_peserta(self, id_sertifikasi):
        """Navigate dengan mengirim ID"""
        self.app.show_page("Input Peserta", id_sertifikasi=id_sertifikasi)
        
    def load_initial_data(self):
        """
        Load HANYA data sertifikasi
        Peserta TIDAK diload di sini
        """
        self.all_sertifikasi = DB_Get_All_Sertifikasi()
        self.update_date_filter_options() 
        self.refresh_display()
        
    def update_date_filter_options(self):
        """Update dropdown tanggal berdasarkan data sertifikasi"""
        if not self.all_sertifikasi:
            dates = ["Semua"]
        else:
            # Extract unique dates dan sort descending
            unique_dates = sorted(
                list(set([s['tanggal_pelatihan'] for s in self.all_sertifikasi])),
                reverse=True
            )
            dates = ["Semua"] + unique_dates
        
        # Update combobox values
        self.date_combo.configure(values=dates)
        
        # Reset ke "Semua" jika tanggal sebelumnya tidak ada lagi
        if self.date_filter not in dates:
            self.date_filter = "Semua"
            self.date_combo.set("Semua")

    def create_widgets(self):
        """Create main layout"""
        # Header section
        self.create_header()
        
        # Control section (search, filter, pagination)
        self.create_controls()
        
        # Tables container (scrollable)
        self.create_tables_container()
    
    def create_header(self):
        """Create page header"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=80)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        header_frame.bind("<Button-1>", lambda e: header_frame.focus_set())
        
        title = ctk.CTkLabel(
            header_frame,
            text="👥 Kelola Peserta",
            font=("Arial", 28, "bold"),
            text_color="#ffffff"
        )
        title.pack(side="left", pady=20)
        title.bind("<Button-1>", lambda e: title.focus_set())

        # Info total sertifikasi
        self.info_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=("Arial", 14),
            text_color="#9e9e9e"
        )
        self.info_label.pack(side="left", padx=20)
        self.info_label.bind("<Button-1>", lambda e: self.info_label.focus_set())
    
    def create_controls(self):
        """Create search, filter, and pagination controls"""
        controls_frame = ctk.CTkFrame(self, fg_color="#1f1f1f", height=70)
        controls_frame.pack(fill="x", padx=20, pady=(0, 15))
        controls_frame.pack_propagate(False)
        controls_frame.bind("<Button-1>", lambda e: controls_frame.focus_set())
        
        # Left side: Search
        search_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        search_frame.pack(side="left", padx=15, pady=10)
        
        ctk.CTkLabel(
            search_frame,
            text="🔍 Cari:",
            font=("Arial", 13)
        ).pack(side="left", padx=(0, 8))

        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            width=250,
            height=35,
            placeholder_text="Nama, NIK, atau No. Peserta..."
        )
        
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", lambda e: self.apply_search())
        
        # Clear search button
        clear_btn = ctk.CTkButton(
            search_frame,
            text="✕",
            width=35,
            height=35,
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            command=self.clear_search
        )
        clear_btn.pack(side="left", padx=5)
        
        # Date filter
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
                             
        # Refresh button
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
        
        # Add button
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
        """Create scrollable container for tables"""
        self.scroll_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.scroll_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def apply_date_filter(self, selected_value):
        """Filter sertifikasi berdasarkan tanggal yang dipilih"""
        self.date_filter = selected_value
        
        if selected_value == "Semua":
            self.filtered_sertifikasi = self.all_sertifikasi
        else:
            # Filter berdasarkan tanggal
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
        
        # Use filtered data
        if not self.filtered_sertifikasi and self.date_filter == "Semua":
            display_data = self.all_sertifikasi
        else:
            display_data = self.filtered_sertifikasi if self.filtered_sertifikasi else self.all_sertifikasi
        
        # Update info
        total_sertifikasi = len(display_data)
        total_peserta = sum(s['jumlah_peserta'] for s in display_data)
        
        if self.date_filter != "Semua":
            self.info_label.configure(
                text=f"📊 {total_sertifikasi} Sertifikasi | {total_peserta} Total Peserta | 📅 Filter: {self.date_filter}"
            )
        else:
            self.info_label.configure(
                text=f"📊 {total_sertifikasi} Sertifikasi | {total_peserta} Total Peserta"
            )
        
        # Create sertifikasi sections
        if not display_data:
            self.show_empty_state()
            return
        
        for sertif in display_data:
            self.create_sertifikasi_section(sertif)
    
    def show_empty_state(self):
        """Show empty state"""
        empty_frame = ctk.CTkFrame(
            self.scroll_container,
            fg_color="#1f1f1f",
            height=200
        )
        empty_frame.pack(fill="x", pady=50)
        
        if self.date_filter != "Semua":
            message = f"📭 Tidak ada sertifikasi pada tanggal {self.date_filter}"
        else:
            message = "📭 Belum ada data sertifikasi"
            
        ctk.CTkLabel(
            empty_frame,
            text=message,
            font=("Arial", 18, "bold"),
            text_color="#666666"
        ).pack(pady=70)
        
    def create_sertifikasi_section(self, sertif):
        """
        Create collapsible section untuk satu sertifikasi
        Peserta belum diload sampai section di-expand
        """
        id_sertifikasi = sertif['id_sertifikasi']
        tanggal_pelatihan = sertif['tanggal_pelatihan']
        
        # Main container
        section_container = ctk.CTkFrame(
            self.scroll_container,
            fg_color="transparent"
        )
        section_container.pack(fill="x", pady=(0, 15))
        section_container.bind("<Button-1>", lambda e: section_container.focus_set())
        
        # Header (clickable untuk expand/collapse)
        header_frame = ctk.CTkFrame(
            section_container,
            fg_color="#1a73e8",
            height=80,
            cursor="hand2"
        )
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Make header clickable
        header_frame.bind(
            "<Button-1>",
            lambda e: (self.toggle_section(id_sertifikasi, section_container),section_container.focus_set())
        )
        
        # 🔥 LEFT SIDE: Arrow + Nama
        left_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="y", padx=(15, 0))
        
        # Arrow icon
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
        
        center_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        center_frame.pack(side="left", expand=True, padx=30)
        
        date_label = ctk.CTkLabel(
            center_frame,
            text=f"📅 {tanggal_pelatihan}",
            font=("Arial", 14, "bold"),
            text_color="white",
            cursor="hand2"
        )
        date_label.pack(side="left", padx=(0, 40))  # Gap 40px ke jumlah peserta
        date_label.bind(
            "<Button-1>",
            lambda e: (self.toggle_section(id_sertifikasi, section_container),section_container.focus_set())
        )
        
        # Jumlah peserta
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
        
        # 🔥 RIGHT SIDE: Action Buttons
        actions_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        actions_frame.pack(side="right", padx=10)
        
        # Add Peserta Button
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
        
        # Update Button
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
        
        # Delete Button
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
        
        # Content frame (initially hidden)
        content_frame = ctk.CTkFrame(section_container, fg_color="#1f1f1f")
        
        # Store references
        section_container._id_sertifikasi = id_sertifikasi
        section_container._content_frame = content_frame
        section_container._arrow_label = arrow_label
        section_container._is_expanded = False
        
    def toggle_section(self, id_sertifikasi, container):
        """
        Toggle section visibility
        LAZY LOAD peserta saat pertama kali di-expand
        """
        is_expanded = container._is_expanded
        
        if is_expanded:
            # Collapse
            container._content_frame.pack_forget()
            container._arrow_label.configure(text="▶")
            container._is_expanded = False
            self.expanded_sections.discard(id_sertifikasi)
        else:
            # Expand
            # Load peserta jika belum ada di cache
            if id_sertifikasi not in self.peserta_cache:
                self.load_peserta_for_sertifikasi(id_sertifikasi)
            
            # Render table
            self.render_peserta_table(container._content_frame, id_sertifikasi)
            
            # Show content
            container._content_frame.pack(fill="x", pady=(2, 0))
            container._arrow_label.configure(text="▼")
            container._is_expanded = True
            self.expanded_sections.add(id_sertifikasi)
    
    def load_peserta_for_sertifikasi(self, id_sertifikasi):
        """
        LAZY LOAD peserta untuk sertifikasi tertentu
        Dipanggil hanya saat section pertama kali di-expand
        """
        try:
            peserta_list = DB_Get_Peserta_By_Sertifikasi(id_sertifikasi)
            self.peserta_cache[id_sertifikasi] = peserta_list
            
            print(f"✓ Loaded {len(peserta_list)} peserta for {id_sertifikasi}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal load peserta: {str(e)}")
            self.peserta_cache[id_sertifikasi] = []
            
    def render_peserta_table(self, content_frame, id_sertifikasi):
        """Render tabel peserta di dalam content frame"""
        # Clear existing content
        for widget in content_frame.winfo_children():
            widget.destroy()
        
        # Get peserta from cache
        peserta_list = self.peserta_cache.get(id_sertifikasi, [])
        
        if not peserta_list:
            # Empty state
            empty_label = ctk.CTkLabel(
                content_frame,
                text="📭 Tidak ada peserta",
                font=("Arial", 14),
                text_color="#666666"
            )
            empty_label.pack(pady=30)
            return
        
        # Action panel
        self.create_action_panel(content_frame, id_sertifikasi)
        
        # Table headers
        self.create_table_headers(content_frame)
        
        # Table rows
        for index,peserta in enumerate(peserta_list,start=1):
            self.create_table_row(content_frame, index, peserta, id_sertifikasi)  
    
    def create_action_panel(self, parent, id_sertifikasi):
        """Create action panel dengan delete button"""
        panel = ctk.CTkFrame(parent, fg_color="#d32f2f", height=50, corner_radius=10)
        panel.pack(fill="x", padx=10, pady=10)
        panel.pack_propagate(False)
        
        # Delete button
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
        
        # Selected count
        count = len(self.selected_ids.get(id_sertifikasi, set()))
        count_label = ctk.CTkLabel(
            panel,
            text=f"Terpilih: {count} item",
            font=("Arial", 13, "bold"),
            text_color="white"
        )
        count_label.pack(side="left", padx=10)
        
        # Store reference
        parent._action_panel = panel
        parent._count_label = count_label
    
    def create_table_headers(self, parent):
        """Create table headers dengan fixed width"""
        header_frame = ctk.CTkFrame(parent, fg_color="#333333", height=45)
        header_frame.pack(fill="x", padx=10, pady=(0, 2))
        header_frame.pack_propagate(False)
        
        # Grid configuration dengan fixed width
        header_frame.grid_columnconfigure(0, weight=0, minsize=65)   # Checkbox
        header_frame.grid_columnconfigure(1, weight=0, minsize=50)   # No
        header_frame.grid_columnconfigure(2, weight=0, minsize=180)  # Nama
        header_frame.grid_columnconfigure(3, weight=0, minsize=150)  # Instansi
        header_frame.grid_columnconfigure(4, weight=0, minsize=180)  # Skema
        header_frame.grid_columnconfigure(5, weight=0, minsize=160)  # NIK
        header_frame.grid_columnconfigure(6, weight=0, minsize=190)  # Tempat/Tgl Lahir
        header_frame.grid_columnconfigure(7, weight=0, minsize=270)  # Alamat
        header_frame.grid_columnconfigure(8, weight=0, minsize=125)  # No HP
        header_frame.grid_columnconfigure(9, weight=0, minsize=100)  # Pendidikan
        
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
                header_frame,
                text=header_text,
                font=("Arial", 13, "bold"),
                text_color="#ffffff",
                anchor="w"
            )
            label.grid(row=0, column=col_index, padx=5, sticky="w")
            
    def create_table_row(self, parent, index, peserta: PesertaModel, id_sertifikasi):
        """Create table row dengan fixed width dan text wrapping"""
        row_frame = ctk.CTkFrame(parent, fg_color="#2a2a2a")
        row_frame.pack(fill="x", padx=10, pady=1)
        
        # Grid configuration - SAMA dengan header
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
        
        # Checkbox
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
            (peserta.nama, 2, 12, 135),        # 180 - 45
            (peserta.instansi, 3, 12, 105),    # 150 - 45
            (peserta.skema, 4, 12, 135),        # 180 - 45
            (peserta.nik[:16] if peserta.nik else "", 5, 12, 0),
            (exportExcel.format_tempat_tanggal(peserta.tempat_lahir, peserta.tanggal_lahir),6, 12, 145),     # 190 - 45
            (exportExcel.format_alamat(peserta), 7, 12, 205),  # 🔥 270 - 45
            (peserta.telepon, 8, 12, 0),
            (peserta.pendidikan, 9, 12, 70),   # 100 - 30
        ]

        
        for cell_text, col_index, font_size, wrap_length in cells_config:
            # Pastikan cell_text tidak None
            display_text = str(cell_text) if cell_text else ""
            
            label = ctk.CTkLabel(
                row_frame,
                text=display_text,
                font=("Arial", font_size),
                text_color="#ffffff",
                anchor="nw",  # north-west untuk top-left alignment
                justify="left",
                wraplength=wrap_length  # Text akan wrap otomatis
            )
            label.grid(row=0, column=col_index, padx=5, pady=5, sticky="nw")
            
    def toggle_selection(self, peserta_id, var, id_sertifikasi):
        """Toggle item selection"""
        for other_id in list(self.selected_ids.keys()):
            if other_id != id_sertifikasi and self.selected_ids[other_id]:
                # Ada selection di sertifikasi lain, clear dulu
                self.selected_ids[other_id].clear()
                self.update_action_panel(other_id)
                
        if id_sertifikasi not in self.selected_ids:
            self.selected_ids[id_sertifikasi] = set()
        
        if var.get():
            self.selected_ids[id_sertifikasi].add(peserta_id) 
        else:
            self.selected_ids[id_sertifikasi].discard(peserta_id)
        
        # Update action panels
        self.update_action_panel(id_sertifikasi)
    
    def update_action_panel(self, id_sertifikasi):
        """Update semua action panel count"""
        for widget in self.scroll_container.winfo_children():
            if (hasattr(widget, '_id_sertifikasi') and 
                widget._id_sertifikasi == id_sertifikasi):
                content = widget._content_frame
                if hasattr(content, '_count_label'):
                    # Hitung selected untuk sertifikasi ini saja
                    count = len(self.selected_ids.get(id_sertifikasi, set()))
                    content._count_label.configure(
                        text=f"Terpilih: {count} item"
                    )
                break
    
    def delete_selected(self, id_sertifikasi):
        """Delete selected peserta"""
        selected_in_this_sertifikasi = self.selected_ids.get(id_sertifikasi, set())
        
        if not self.selected_ids:
            messagebox.showinfo("Info", "Tidak ada item yang dipilih!")
            return
        
        result = messagebox.askyesno(
            "Konfirmasi",
            f"Hapus {len(self.selected_ids)} peserta terpilih?\n\nData tidak dapat dikembalikan!"
        )
        
        if result:
            try:
                # Get NIK list
                peserta_list = self.peserta_cache.get(id_sertifikasi, [])
                nik_list = [
                    p['nik'] for p in peserta_list 
                    if p['id'] in selected_in_this_sertifikasi
                ]
                
                # Delete from database
                deleted = DB_Delete_Peserta_Batch(nik_list)
                
                if deleted > 0:
                    # Remove from cache
                    self.peserta_cache[id_sertifikasi] = [
                        p for p in peserta_list 
                        if p['id'] not in self.selected_ids
                    ]
                    
                    # Clear selection
                    self.selected_ids.clear()
                    
                    # Refresh display
                    self.refresh_all()
                    
                    messagebox.showinfo("Sukses", f"{deleted} peserta berhasil dihapus!")
                else:
                    messagebox.showwarning("Warning", "Tidak ada data yang dihapus")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menghapus data: {str(e)}")
    
    def apply_search(self):
        """Apply search filter (not implemented in this version)"""
        self.search_text = self.search_entry.get().strip().lower()
        
        if not self.search_text:
            return
        
        # TODO: Implement search across all peserta
        # Could use DB_Search_Peserta() function
        messagebox.showinfo(
            "Search",
            f"Fitur pencarian untuk '{self.search_text}' akan segera ditambahkan"
        )
    
    def clear_search(self):
        """Clear search"""
        self.search_entry.delete(0, 'end')
        self.search_text = ""
    
    def refresh_all(self):
        """
        Refresh complete:
        - Reload sertifikasi
        - Clear cache
        - Reset expanded sections
        """
        # Clear cache
        self.peserta_cache.clear()
        self.selected_ids.clear()
        
        # Remember expanded sections
        expanded_before = self.expanded_sections.copy()
        self.expanded_sections.clear()
        
        # Reload sertifikasi
        self.all_sertifikasi = DB_Get_All_Sertifikasi()
        self.update_date_filter_options()
        
        # Refresh display
        self.refresh_display()
        
        # Re-expand previously expanded sections
        for id_sertifikasi in expanded_before:
            for widget in self.scroll_container.winfo_children():
                if (hasattr(widget, '_id_sertifikasi') and 
                    widget._id_sertifikasi == id_sertifikasi):
                    self.toggle_section(id_sertifikasi, widget)
                    break
                
    def show_add_sertifikasi_dialog(self, sertif=None):
        """Show custom dialog untuk tambah sertifikasi baru"""
        if sertif == None:
            AddSertifikasiDialog(self, self.on_sertifikasi_added)
        else:
            AddSertifikasiDialog(self, self.on_sertifikasi_added, sertif)
    
    def on_sertifikasi_added(self):
        """Callback setelah sertifikasi berhasil ditambahkan"""
        self.refresh_all()
        
    def delete_sertifikasi(self, id_sertifikasi):
        if messagebox.askyesno("Konfirmasi", f"Konfirmasi Untuk Hapus?"):
            DB_Delete_Sertifikasi(id_sertifikasi,True)
            self.refresh_all()
        
    def export_sertifikasi(self, id_sertifikasi,tanggal_pelatihan: str):
        peserta = DB_Get_Peserta_By_Sertifikasi(id_sertifikasi)
        download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        OUTPUT_DIR = os.path.join(download_dir, "AL-AWAL EXPORT")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        exportExcel.export_peserta_to_excel(peserta,f"{OUTPUT_DIR}[AWL] Peserta BNSP - {tanggal_pelatihan.replace("/","-")}.xlsx")       
        
    def show_import_dialog(self,id_sertifikasi):
        """Show import dialog"""
        from pages.import_dialog import ImportDialog
        ImportDialog(self, self.refresh_all, id_sertifikasi)    
        
    def show_menu_dropdown(self, id_sertifikasi, tanggal_pelatihan, button):
        """Show dropdown menu dengan opsi Import, Ekspor, Salin"""
        # Create dropdown window
        menu = ctk.CTkToplevel(self)
        menu.title("")
        menu.overrideredirect(True)  # Remove window decorations
        menu.configure(fg_color="#1f1f1f")
        
        # Position below button - GESER KE KIRI
        menu_width = 150
        x = button.winfo_rootx() - menu_width + button.winfo_width() -40  # 🔥 Align kanan menu dengan kanan button
        y = button.winfo_rooty() + button.winfo_height()
        menu.geometry(f"{menu_width}x120+{x}+{y}")
        
        # Make it stay on top
        menu.attributes('-topmost', True)
        menu.transient(self)
        
        # Menu items
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
        
        # Close menu when clicking outside
        def close_menu(event):
            if event.widget != menu:
                menu.destroy()
        
        self.after(100, lambda: menu.bind_all("<Button-1>", close_menu, add="+"))

    def show_export_dialog(self, id_sertifikasi, tanggal_pelatihan):
        """Show export dialog"""
        from pages.export_dialog import ExportDialog
        from services.database import DB_Get_Peserta_By_Sertifikasi
        
        # Load peserta
        peserta_list = DB_Get_Peserta_By_Sertifikasi(id_sertifikasi)
        
        if not peserta_list:
            messagebox.showinfo("Info", "Tidak ada peserta untuk diekspor!")
            return
        
        sertifikasi_info = {
            'id_sertifikasi': id_sertifikasi,
            'tanggal_pelatihan': tanggal_pelatihan
        }
        
        ExportDialog(self, peserta_list, sertifikasi_info, self.refresh_all)

    def copy_peserta_data(self, id_sertifikasi):
        """Copy peserta data dalam format AWL-Copy yang bisa di-import"""
        from services.database import DB_Get_Peserta_By_Sertifikasi, DB_Get_Sertifikasi_By_ID
        
        # Get sertifikasi info
        sertif = DB_Get_Sertifikasi_By_ID(id_sertifikasi)
        if not sertif:
            messagebox.showerror("Error", "Sertifikasi tidak ditemukan!")
            return
        
        # Get peserta
        peserta_list = DB_Get_Peserta_By_Sertifikasi(id_sertifikasi)
        
        if not peserta_list:
            messagebox.showinfo("Info", "Tidak ada peserta untuk disalin!")
            return
        
        def wrap(val):
            """Wrap value dengan delimiter ⟦...⟧"""
            return f"⟦{str(val).replace('⟦','').replace('⟧','')}⟧"

        # Build data lines
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

        # Build header
        header = "".join([
            wrap("AWL-Copy"),
            wrap(sertif["sertifikasi"]),
            wrap(sertif["tanggal_pelatihan"]),
        ])

        # Combine header and data
        result_text = header + "\n" + "\n".join(lines)

        # Copy to clipboard
        self.clipboard_clear()
        self.clipboard_append(result_text)
        
        messagebox.showinfo(
            "Sukses",
            f"✅ {len(peserta_list)} peserta berhasil disalin!\n\n"
            f"Format: AWL-Copy\n"
            f"Data sudah ada di clipboard.\n\n"
            f"Paste di dialog Import dengan format 'AWL-Copy'."
        )
        
        