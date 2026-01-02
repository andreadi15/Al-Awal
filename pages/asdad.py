# import customtkinter as ctk
# from tkinter import messagebox
# from datetime import datetime
# import re
# from services.database import (
#     DB_Get_All_Sertifikasi,
#     DB_Get_Peserta_By_Sertifikasi,
#     DB_Delete_Peserta_Batch,
#     DB_Search_Peserta
# )

# class PesertaPage(ctk.CTkFrame):
#     def __init__(self, parent):
#         super().__init__(parent, fg_color="#2a2a2a")
        
#         # Data sertifikasi (loaded at start)
#         self.all_sertifikasi = []
        
#         # Cache peserta (lazy loaded)
#         # Format: {id_sertifikasi: [peserta_list]}
#         self.peserta_cache = {}
        
#         # State management
#         self.selected_ids = set()
#         self.expanded_sections = set()  # Track yang sudah di-expand
#         self.search_text = ""
#         self.date_filter = "Semua"  # Track filter tanggal
#         self.filtered_sertifikasi = []  # Data sertifikasi yang sudah difilter
        
#         self.create_widgets()
#         self.load_initial_data()
    
#     def load_initial_data(self):
#         """
#         Load HANYA data sertifikasi
#         Peserta TIDAK diload di sini
#         """
#         self.all_sertifikasi = DB_Get_All_Sertifikasi()
#         self.update_date_filter_options()
#         self.apply_date_filter()
    
#     def update_date_filter_options(self):
#         """Update dropdown tanggal berdasarkan data sertifikasi"""
#         if not self.all_sertifikasi:
#             dates = ["Semua"]
#         else:
#             # Extract unique dates dan sort descending
#             unique_dates = sorted(
#                 list(set([s['tanggal_pelatihan'] for s in self.all_sertifikasi])),
#                 reverse=True
#             )
#             dates = ["Semua"] + unique_dates
        
#         # Update combobox values
#         self.date_combo.configure(values=dates)
        
#         # Reset ke "Semua" jika tanggal sebelumnya tidak ada lagi
#         if self.date_filter not in dates:
#             self.date_filter = "Semua"
#             self.date_combo.set("Semua")
    
#     def create_widgets(self):
#         """Create main layout"""
#         # Header section
#         self.create_header()
        
#         # Control section (search only)
#         self.create_controls()
        
#         # Tables container (scrollable)
#         self.create_tables_container()
    
#     def create_header(self):
#         """Create page header"""
#         header_frame = ctk.CTkFrame(self, fg_color="transparent", height=80)
#         header_frame.pack(fill="x", padx=20, pady=(20, 10))
#         header_frame.pack_propagate(False)
        
#         title = ctk.CTkLabel(
#             header_frame,
#             text="👥 Kelola Peserta",
#             font=("Arial", 28, "bold"),
#             text_color="#ffffff"
#         )
#         title.pack(side="left", pady=20)
        
#         # Info total sertifikasi
#         self.info_label = ctk.CTkLabel(
#             header_frame,
#             text="",
#             font=("Arial", 14),
#             text_color="#9e9e9e"
#         )
#         self.info_label.pack(side="left", padx=20)
        
#         # Add button
#         add_btn = ctk.CTkButton(
#             header_frame,
#             text="➕ Tambah Sertifikasi",
#             width=180,
#             height=40,
#             font=("Arial", 14, "bold"),
#             fg_color="#4caf50",
#             hover_color="#45a049",
#             corner_radius=10,
#             command=self.show_add_sertifikasi_dialog
#         )
#         add_btn.pack(side="right", pady=20)
    
#     def create_controls(self):
#         """Create search and filter controls"""
#         controls_frame = ctk.CTkFrame(self, fg_color="#1f1f1f", height=70)
#         controls_frame.pack(fill="x", padx=20, pady=(0, 15))
#         controls_frame.pack_propagate(False)
        
#         # Search
#         search_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
#         search_frame.pack(side="left", padx=15, pady=10)
        
#         ctk.CTkLabel(
#             search_frame,
#             text="🔍 Cari Peserta:",
#             font=("Arial", 13)
#         ).pack(side="left", padx=(0, 8))
        
#         self.search_entry = ctk.CTkEntry(
#             search_frame,
#             width=250,
#             height=35,
#             placeholder_text="Nama, NIK, atau No. Peserta..."
#         )
#         self.search_entry.pack(side="left", padx=5)
#         self.search_entry.bind("<KeyRelease>", lambda e: self.apply_search())
        
#         # Clear search button
#         clear_btn = ctk.CTkButton(
#             search_frame,
#             text="✕",
#             width=35,
#             height=35,
#             fg_color="#d32f2f",
#             hover_color="#b71c1c",
#             command=self.clear_search
#         )
#         clear_btn.pack(side="left", padx=5)
        
#         # Date filter
#         date_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
#         date_frame.pack(side="left", padx=15, pady=10)
        
#         ctk.CTkLabel(
#             date_frame,
#             text="📅 Tanggal:",
#             font=("Arial", 13)
#         ).pack(side="left", padx=(0, 8))
        
#         self.date_combo = ctk.CTkComboBox(
#             date_frame,
#             values=["Semua"],
#             width=150,
#             height=35,
#             command=lambda x: self.apply_date_filter()
#         )
#         self.date_combo.set("Semua")
#         self.date_combo.pack(side="left")
        
#         # Refresh button
#         refresh_btn = ctk.CTkButton(
#             controls_frame,
#             text="🔄 Refresh",
#             width=100,
#             height=35,
#             fg_color="#1a73e8",
#             hover_color="#1557b0",
#             command=self.refresh_all
#         )
#         refresh_btn.pack(side="right", padx=15)
    
#     def create_tables_container(self):
#         """Create scrollable container for tables"""
#         self.scroll_container = ctk.CTkScrollableFrame(
#             self,
#             fg_color="transparent"
#         )
#         self.scroll_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
#     def refresh_display(self):
#         """Refresh display dengan data sertifikasi yang sudah difilter"""
#         # Clear existing
#         for widget in self.scroll_container.winfo_children():
#             widget.destroy()
        
#         # Use filtered data
#         display_data = self.filtered_sertifikasi
        
#         # Update info
#         total_sertifikasi = len(display_data)
#         total_peserta = sum(s['jumlah_peserta'] for s in display_data)
        
#         if self.date_filter != "Semua":
#             self.info_label.configure(
#                 text=f"📊 {total_sertifikasi} Sertifikasi | {total_peserta} Total Peserta | 📅 Filter: {self.date_filter}"
#             )
#         else:
#             self.info_label.configure(
#                 text=f"📊 {total_sertifikasi} Sertifikasi | {total_peserta} Total Peserta"
#             )
        
#         # Create sertifikasi sections
#         if not display_data:
#             self.show_empty_state()
#             return
        
#         for sertif in display_data:
#             self.create_sertifikasi_section(sertif)
    
#     def show_empty_state(self):
#         """Show empty state"""
#         empty_frame = ctk.CTkFrame(
#             self.scroll_container,
#             fg_color="#1f1f1f",
#             height=200
#         )
#         empty_frame.pack(fill="x", pady=50)
        
#         if self.date_filter != "Semua":
#             message = f"📭 Tidak ada sertifikasi pada tanggal {self.date_filter}"
#         else:
#             message = "📭 Belum ada data sertifikasi"
        
#         ctk.CTkLabel(
#             empty_frame,
#             text=message,
#             font=("Arial", 18, "bold"),
#             text_color="#666666"
#         ).pack(pady=70)
    
#     def create_sertifikasi_section(self, sertif):
#         """
#         Create collapsible section untuk satu sertifikasi
#         Peserta belum diload sampai section di-expand
#         """
#         id_sertifikasi = sertif['id_sertifikasi']
        
#         # Main container
#         section_container = ctk.CTkFrame(
#             self.scroll_container,
#             fg_color="transparent"
#         )
#         section_container.pack(fill="x", pady=(0, 15))
        
#         # Header (clickable untuk expand/collapse)
#         header_frame = ctk.CTkFrame(
#             section_container,
#             fg_color="#1a73e8",
#             height=60,
#             cursor="hand2"
#         )
#         header_frame.pack(fill="x")
#         header_frame.pack_propagate(False)
        
#         # Make header clickable
#         header_frame.bind(
#             "<Button-1>",
#             lambda e: self.toggle_section(id_sertifikasi, section_container)
#         )
        
#         # Arrow icon
#         arrow_label = ctk.CTkLabel(
#             header_frame,
#             text="▶",
#             font=("Arial", 18, "bold"),
#             text_color="white",
#             cursor="hand2"
#         )
#         arrow_label.pack(side="left", padx=15)
#         arrow_label.bind(
#             "<Button-1>",
#             lambda e: self.toggle_section(id_sertifikasi, section_container)
#         )
        
#         # Sertifikasi info
#         info_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
#         info_frame.pack(side="left", fill="x", expand=True, padx=10)
#         info_frame.bind(
#             "<Button-1>",
#             lambda e: self.toggle_section(id_sertifikasi, section_container)
#         )
        
#         # Nama sertifikasi
#         name_label = ctk.CTkLabel(
#             info_frame,
#             text=f"📜 {sertif['sertifikasi']}",
#             font=("Arial", 16, "bold"),
#             text_color="white",
#             anchor="w",
#             cursor="hand2"
#         )
#         name_label.pack(side="left", fill="x", expand=True)
#         name_label.bind(
#             "<Button-1>",
#             lambda e: self.toggle_section(id_sertifikasi, section_container)
#         )
        
#         # Tanggal
#         date_label = ctk.CTkLabel(
#             info_frame,
#             text=f"📅 {sertif['tanggal_pelatihan']}",
#             font=("Arial", 13),
#             text_color="#e0e0e0",
#             cursor="hand2"
#         )
#         date_label.pack(side="left", padx=20)
#         date_label.bind(
#             "<Button-1>",
#             lambda e: self.toggle_section(id_sertifikasi, section_container)
#         )
        
#         # Jumlah peserta
#         count_label = ctk.CTkLabel(
#             info_frame,
#             text=f"👥 {sertif['jumlah_peserta']} peserta",
#             font=("Arial", 13, "bold"),
#             text_color="#ffeb3b",
#             cursor="hand2"
#         )
#         count_label.pack(side="left", padx=10)
#         count_label.bind(
#             "<Button-1>",
#             lambda e: self.toggle_section(id_sertifikasi, section_container)
#         )
        
#         # Content frame (initially hidden)
#         content_frame = ctk.CTkFrame(section_container, fg_color="#1f1f1f")
#         # Don't pack yet - will be shown when expanded
        
#         # Store references
#         section_container._id_sertifikasi = id_sertifikasi
#         section_container._content_frame = content_frame
#         section_container._arrow_label = arrow_label
#         section_container._is_expanded = False
    
#     def toggle_section(self, id_sertifikasi, container):
#         """
#         Toggle section visibility
#         LAZY LOAD peserta saat pertama kali di-expand
#         """
#         is_expanded = container._is_expanded
        
#         if is_expanded:
#             # Collapse
#             container._content_frame.pack_forget()
#             container._arrow_label.configure(text="▶")
#             container._is_expanded = False
#             self.expanded_sections.discard(id_sertifikasi)
#         else:
#             # Expand
#             # Load peserta jika belum ada di cache
#             if id_sertifikasi not in self.peserta_cache:
#                 self.load_peserta_for_sertifikasi(id_sertifikasi)
            
#             # Render table
#             self.render_peserta_table(container._content_frame, id_sertifikasi)
            
#             # Show content
#             container._content_frame.pack(fill="x", pady=(2, 0))
#             container._arrow_label.configure(text="▼")
#             container._is_expanded = True
#             self.expanded_sections.add(id_sertifikasi)
    
#     def load_peserta_for_sertifikasi(self, id_sertifikasi):
#         """
#         LAZY LOAD peserta untuk sertifikasi tertentu
#         Dipanggil hanya saat section pertama kali di-expand
#         """
#         try:
#             peserta_list = DB_Get_Peserta_By_Sertifikasi(id_sertifikasi)
#             self.peserta_cache[id_sertifikasi] = peserta_list
            
#             print(f"✓ Loaded {len(peserta_list)} peserta for {id_sertifikasi}")
#         except Exception as e:
#             messagebox.showerror("Error", f"Gagal load peserta: {str(e)}")
#             self.peserta_cache[id_sertifikasi] = []
    
#     def render_peserta_table(self, content_frame, id_sertifikasi):
#         """Render tabel peserta di dalam content frame"""
#         # Clear existing content
#         for widget in content_frame.winfo_children():
#             widget.destroy()
        
#         # Get peserta from cache
#         peserta_list = self.peserta_cache.get(id_sertifikasi, [])
        
#         if not peserta_list:
#             # Empty state
#             empty_label = ctk.CTkLabel(
#                 content_frame,
#                 text="📭 Tidak ada peserta",
#                 font=("Arial", 14),
#                 text_color="#666666"
#             )
#             empty_label.pack(pady=30)
#             return
        
#         # Action panel
#         self.create_action_panel(content_frame, id_sertifikasi)
        
#         # Table headers
#         self.create_table_headers(content_frame)
        
#         # Table rows
#         for peserta in peserta_list:
#             self.create_table_row(content_frame, peserta)
    
#     def create_action_panel(self, parent, id_sertifikasi):
#         """Create action panel dengan delete button"""
#         panel = ctk.CTkFrame(parent, fg_color="#d32f2f", height=50, corner_radius=10)
#         panel.pack(fill="x", padx=10, pady=10)
#         panel.pack_propagate(False)
        
#         # Delete button
#         delete_btn = ctk.CTkButton(
#             panel,
#             text="🗑️ Hapus Terpilih",
#             width=140,
#             height=35,
#             fg_color="#b71c1c",
#             hover_color="#8b0000",
#             corner_radius=8,
#             command=lambda: self.delete_selected(id_sertifikasi)
#         )
#         delete_btn.pack(side="left", padx=15)
        
#         # Selected count
#         count_label = ctk.CTkLabel(
#             panel,
#             text=f"Terpilih: {len(self.selected_ids)} item",
#             font=("Arial", 13, "bold"),
#             text_color="white"
#         )
#         count_label.pack(side="left", padx=10)
        
#         # Store reference
#         parent._action_panel = panel
#         parent._count_label = count_label
    
#     def create_table_headers(self, parent):
#         """Create table headers"""
#         header_frame = ctk.CTkFrame(parent, fg_color="#333333", height=45)
#         header_frame.pack(fill="x", padx=10, pady=(0, 2))
#         header_frame.pack_propagate(False)
        
#         # Grid configuration
#         header_frame.grid_columnconfigure(0, weight=0, minsize=50)   # Checkbox
#         header_frame.grid_columnconfigure(1, weight=1, minsize=60)   # No
#         header_frame.grid_columnconfigure(2, weight=3, minsize=200)  # Nama
#         header_frame.grid_columnconfigure(3, weight=2, minsize=150)  # NIK
#         header_frame.grid_columnconfigure(4, weight=2, minsize=120)  # Skema
#         header_frame.grid_columnconfigure(5, weight=2, minsize=120)  # Instansi
        
#         headers = ["☑", "No", "Nama Peserta", "NIK", "Skema", "Instansi"]
#         for i, header in enumerate(headers):
#             label = ctk.CTkLabel(
#                 header_frame,
#                 text=header,
#                 font=("Arial", 13, "bold"),
#                 text_color="#ffffff"
#             )
#             label.grid(row=0, column=i, padx=10, sticky="w")
    
#     def create_table_row(self, parent, peserta):
#         """Create table row untuk satu peserta"""
#         row_frame = ctk.CTkFrame(parent, fg_color="#2a2a2a", height=50)
#         row_frame.pack(fill="x", padx=10, pady=1)
#         row_frame.pack_propagate(False)
        
#         # Grid configuration
#         row_frame.grid_columnconfigure(0, weight=0, minsize=50)
#         row_frame.grid_columnconfigure(1, weight=1, minsize=60)
#         row_frame.grid_columnconfigure(2, weight=3, minsize=200)
#         row_frame.grid_columnconfigure(3, weight=2, minsize=150)
#         row_frame.grid_columnconfigure(4, weight=2, minsize=120)
#         row_frame.grid_columnconfigure(5, weight=2, minsize=120)
        
#         # Checkbox
#         peserta_id = peserta['id']
#         check_var = ctk.BooleanVar(value=peserta_id in self.selected_ids)
#         checkbox = ctk.CTkCheckBox(
#             row_frame,
#             text="",
#             width=30,
#             variable=check_var,
#             command=lambda: self.toggle_selection(peserta_id, check_var)
#         )
#         checkbox.grid(row=0, column=0, padx=15)
        
#         # Data cells
#         cells = [
#             str(peserta['id']),
#             peserta['nama'],
#             peserta['nik'],
#             peserta['skema'],
#             peserta['instansi']
#         ]
        
#         for i, cell in enumerate(cells, start=1):
#             label = ctk.CTkLabel(
#                 row_frame,
#                 text=cell,
#                 font=("Arial", 12),
#                 text_color="#ffffff",
#                 anchor="w"
#             )
#             label.grid(row=0, column=i, padx=10, sticky="w")
    
#     def toggle_selection(self, peserta_id, var):
#         """Toggle item selection"""
#         if var.get():
#             self.selected_ids.add(peserta_id)
#         else:
#             self.selected_ids.discard(peserta_id)
        
#         # Update action panels
#         self.update_action_panels()
    
#     def update_action_panels(self):
#         """Update semua action panel count"""
#         for widget in self.scroll_container.winfo_children():
#             if hasattr(widget, '_content_frame'):
#                 content = widget._content_frame
#                 if hasattr(content, '_count_label'):
#                     content._count_label.configure(
#                         text=f"Terpilih: {len(self.selected_ids)} item"
#                     )
    
#     def delete_selected(self, id_sertifikasi):
#         """Delete selected peserta"""
#         if not self.selected_ids:
#             messagebox.showinfo("Info", "Tidak ada item yang dipilih!")
#             return
        
#         result = messagebox.askyesno(
#             "Konfirmasi",
#             f"Hapus {len(self.selected_ids)} peserta terpilih?\n\nData tidak dapat dikembalikan!"
#         )
        
#         if result:
#             try:
#                 # Get NIK list
#                 peserta_list = self.peserta_cache.get(id_sertifikasi, [])
#                 nik_list = [
#                     p['nik'] for p in peserta_list 
#                     if p['id'] in self.selected_ids
#                 ]
                
#                 # Delete from database
#                 deleted = DB_Delete_Peserta_Batch(nik_list)
                
#                 if deleted > 0:
#                     # Remove from cache
#                     self.peserta_cache[id_sertifikasi] = [
#                         p for p in peserta_list 
#                         if p['id'] not in self.selected_ids
#                     ]
                    
#                     # Clear selection
#                     self.selected_ids.clear()
                    
#                     # Refresh display
#                     self.refresh_all()
                    
#                     messagebox.showinfo("Sukses", f"{deleted} peserta berhasil dihapus!")
#                 else:
#                     messagebox.showwarning("Warning", "Tidak ada data yang dihapus")
                    
#             except Exception as e:
#                 messagebox.showerror("Error", f"Gagal menghapus data: {str(e)}")
    
#     def apply_date_filter(self):
#         """
#         Apply filter tanggal
#         Hanya filter data sertifikasi, peserta tetap lazy load
#         """
#         self.date_filter = self.date_combo.get()
        
#         if self.date_filter == "Semua":
#             # Show all
#             self.filtered_sertifikasi = self.all_sertifikasi.copy()
#         else:
#             # Filter by date
#             self.filtered_sertifikasi = [
#                 s for s in self.all_sertifikasi 
#                 if s['tanggal_pelatihan'] == self.date_filter
#             ]
        
#         # Clear expanded sections dan cache untuk tanggal yang tidak ditampilkan
#         if self.date_filter != "Semua":
#             # Hanya keep cache untuk sertifikasi yang ditampilkan
#             displayed_ids = {s['id_sertifikasi'] for s in self.filtered_sertifikasi}
#             self.expanded_sections = self.expanded_sections.intersection(displayed_ids)
        
#         # Refresh display
#         self.refresh_display()
    
#     def apply_search(self):
#         """Apply search filter"""
#         self.search_text = self.search_entry.get().strip().lower()
        
#         if not self.search_text:
#             return
        
#         # Search akan dilakukan per section saat expanded
#         # Untuk sekarang beri info
#         messagebox.showinfo(
#             "Info Pencarian",
#             f"Pencarian '{self.search_text}'\n\n"
#             "Tips: Expand section sertifikasi untuk melihat peserta yang sesuai dengan pencarian"
#         )
    
#     def clear_search(self):
#         """Clear search"""
#         self.search_entry.delete(0, 'end')
#         self.search_text = ""
    
#     def clear_date_filter(self):
#         """Reset filter tanggal ke Semua"""
#         self.date_combo.set("Semua")
#         self.apply_date_filter()
    
#     def refresh_all(self):
#         """
#         Refresh complete:
#         - Reload sertifikasi
#         - Update date filter options
#         - Clear cache
#         - Reset expanded sections
#         """
#         # Clear cache
#         self.peserta_cache.clear()
#         self.selected_ids.clear()
        
#         # Remember expanded sections
#         expanded_before = self.expanded_sections.copy()
#         self.expanded_sections.clear()
        
#         # Reload sertifikasi
#         self.all_sertifikasi = DB_Get_All_Sertifikasi()
        
#         # Update date filter dropdown
#         self.update_date_filter_options()
        
#         # Re-apply current filter
#         self.apply_date_filter()
        
#         # Re-expand previously expanded sections
#         for id_sertifikasi in expanded_before:
#             for widget in self.scroll_container.winfo_children():
#                 if (hasattr(widget, '_id_sertifikasi') and 
#                     widget._id_sertifikasi == id_sertifikasi):
#                     self.toggle_section(id_sertifikasi, widget)
#                     break
    
#     def show_add_sertifikasi_dialog(self):
#         """Show custom dialog untuk tambah sertifikasi baru"""
#         AddSertifikasiDialog(self, self.on_sertifikasi_added)
    
#     def on_sertifikasi_added(self):
#         """Callback setelah sertifikasi berhasil ditambahkan"""
#         self.refresh_all()


# # ============================================
# # CUSTOM DIALOG: Tambah Sertifikasi
# # ============================================

# class AddSertifikasiDialog(ctk.CTkToplevel):
#     """
#     Custom dialog untuk menambah sertifikasi baru
#     Matching dengan design main aplikasi
#     """
#     def __init__(self, parent, callback):
#         super().__init__(parent)
        
#         self.callback = callback
        
#         # Window configuration
#         self.title("Tambah Sertifikasi Baru")
#         self.geometry("500x400")
#         self.resizable(False, False)
        
#         # Center window
#         self.update_idletasks()
#         x = (self.winfo_screenwidth() // 2) - (500 // 2)
#         y = (self.winfo_screenheight() // 2) - (400 // 2)
#         self.geometry(f"500x400+{x}+{y}")
        
#         # Make modal
#         self.transient(parent)
#         self.grab_set()
        
#         # Style matching main app
#         self.configure(fg_color="#2a2a2a")
        
#         self.create_widgets()
    
#     def create_widgets(self):
#         """Create dialog content"""
#         # Header
#         header = ctk.CTkFrame(self, fg_color="#1a73e8", height=80)
#         header.pack(fill="x")
#         header.pack_propagate(False)
        
#         ctk.CTkLabel(
#             header,
#             text="➕ Tambah Sertifikasi Baru",
#             font=("Arial", 22, "bold"),
#             text_color="white"
#         ).pack(pady=25)
        
#         # Content frame
#         content = ctk.CTkFrame(self, fg_color="transparent")
#         content.pack(fill="both", expand=True, padx=30, pady=30)
        
#         # Form fields
#         # 1. Jenis Sertifikasi
#         ctk.CTkLabel(
#             content,
#             text="📜 Jenis Sertifikasi",
#             font=("Arial", 14, "bold"),
#             anchor="w"
#         ).pack(fill="x", pady=(0, 8))
        
#         self.sertifikasi_entry = ctk.CTkEntry(
#             content,
#             height=45,
#             font=("Arial", 13),
#             placeholder_text="Contoh: BNSP Basic Safety Training"
#         )
#         self.sertifikasi_entry.pack(fill="x", pady=(0, 20))
        
#         # 2. Tanggal Pelatihan
#         ctk.CTkLabel(
#             content,
#             text="📅 Tanggal Pelatihan",
#             font=("Arial", 14, "bold"),
#             anchor="w"
#         ).pack(fill="x", pady=(0, 8))
        
#         date_frame = ctk.CTkFrame(content, fg_color="transparent")
#         date_frame.pack(fill="x", pady=(0, 30))
        
#         self.tanggal_entry = ctk.CTkEntry(
#             date_frame,
#             height=45,
#             font=("Arial", 13),
#             placeholder_text="DD-MM-YYYY"
#         )
#         self.tanggal_entry.pack(fill="x")
        
#         # Bind KeyPress untuk format otomatis
#         self.tanggal_entry.bind("<KeyPress>", self.format_tanggal_pelatihan)
        
#         # Set default tanggal hari ini
#         today = datetime.now()
#         default_date = today.strftime("%d-%m-%Y")
#         self.tanggal_entry.insert(0, default_date)
        
#         # Buttons
#         button_frame = ctk.CTkFrame(content, fg_color="transparent")
#         button_frame.pack(side="bottom", fill="x", pady=10)
        
#         # Cancel button
#         cancel_btn = ctk.CTkButton(
#             button_frame,
#             text="✕ Batal",
#             width=120,
#             height=45,
#             font=("Arial", 14, "bold"),
#             fg_color="#757575",
#             hover_color="#616161",
#             corner_radius=10,
#             command=self.destroy
#         )
#         cancel_btn.pack(side="left", padx=5)
        
#         # Save button
#         save_btn = ctk.CTkButton(
#             button_frame,
#             text="✓ Simpan",
#             width=120,
#             height=45,
#             font=("Arial", 14, "bold"),
#             fg_color="#4caf50",
#             hover_color="#45a049",
#             corner_radius=10,
#             command=self.save_sertifikasi
#         )
#         save_btn.pack(side="right", padx=5)
        
#         # Focus to first field
#         self.sertifikasi_entry.focus()
    
#     def format_tanggal_pelatihan(self, event):
#         """
#         Handler untuk input tanggal pelatihan dengan format DD-MM-YYYY
#         Auto-format saat user mengetik
#         """
#         entry = event.widget
#         current_text = entry.get()
        
#         # Ambil hanya digit dari text saat ini
#         current_digits = re.sub(r'\D', '', current_text)
        
#         # Handle Backspace
#         if event.keysym == "BackSpace":
#             if len(current_digits) > 0:
#                 current_digits = current_digits[:-1]
#             else:
#                 return "break"
#         # Handle input digit
#         elif event.char.isdigit():
#             # Cek apakah sudah mencapai batas 8 digit
#             if len(current_digits) >= 8:
#                 return "break"
#             current_digits += event.char
#         else:
#             # Karakter selain digit atau backspace, block
#             return "break"
        
#         # Format dengan strip: DD-MM-YYYY
#         formatted = ""
#         for i, digit in enumerate(current_digits):
#             if i == 2 or i == 4:
#                 formatted += "-"
#             formatted += digit
        
#         # Update entry
#         entry.delete(0, "end")
#         entry.insert(0, formatted)
        
#         return "break"
    
#     def validate_tanggal(self, tanggal_str):
#         """
#         Validate tanggal format DD-MM-YYYY
#         Return tuple: (is_valid, error_message, formatted_date)
#         """
#         if not tanggal_str or tanggal_str.strip() == "":
#             return (False, "Tanggal tidak boleh kosong!", None)
        
#         # Cek format dengan regex
#         # pattern = r'^\d{2}-\d{2}-\d{4}
    
#     def save_sertifikasi(self):
#         """Validate and save sertifikasi"""
#         from services.database import DB_Save_Sertifikasi
#         import uuid
        
#         # Get values
#         sertifikasi = self.sertifikasi_entry.get().strip()
#         tanggal_input = self.tanggal_entry.get().strip()
        
#         # Validation: Jenis Sertifikasi
#         if not sertifikasi:
#             self.show_error("Jenis sertifikasi tidak boleh kosong!")
#             self.sertifikasi_entry.focus()
#             return
        
#         # Validation: Tanggal
#         is_valid, error_msg, tanggal_pelatihan = self.validate_tanggal(tanggal_input)
#         if not is_valid:
#             self.show_error(error_msg)
#             self.tanggal_entry.focus()
#             return
        
#         # Generate unique ID
#         id_sertifikasi = f"SERT-{uuid.uuid4().hex[:8].upper()}"
        
#         try:
#             # Save to database
#             DB_Save_Sertifikasi(
#                 id_sertifikasi=id_sertifikasi,
#                 sertifikasi=sertifikasi,
#                 tanggal=tanggal_pelatihan  # Format: YYYY-MM-DD
#             )
            
#             # Format tanggal untuk display (DD-MM-YYYY)
#             display_date = datetime.strptime(tanggal_pelatihan, "%Y-%m-%d").strftime("%d-%m-%Y")
            
#             # Show success
#             self.show_success(
#                 f"✓ Sertifikasi berhasil ditambahkan!\n\n"
#                 f"ID: {id_sertifikasi}\n"
#                 f"Jenis: {sertifikasi}\n"
#                 f"Tanggal: {display_date}"
#             )
            
#             # Callback to parent
#             if self.callback:
#                 self.callback()
            
#             # Close dialog
#             self.destroy()
            
#         except Exception as e:
#             self.show_error(f"Gagal menyimpan data!\n\n{str(e)}")
    
#     def show_error(self, message):
#         """Show error message"""
#         error_dialog = ctk.CTkToplevel(self)
#         error_dialog.title("Error")
#         error_dialog.geometry("400x200")
#         error_dialog.resizable(False, False)
#         error_dialog.configure(fg_color="#2a2a2a")
        
#         # Center
#         error_dialog.update_idletasks()
#         x = (error_dialog.winfo_screenwidth() // 2) - 200
#         y = (error_dialog.winfo_screenheight() // 2) - 100
#         error_dialog.geometry(f"400x200+{x}+{y}")
        
#         error_dialog.transient(self)
#         error_dialog.grab_set()
        
#         # Header
#         header = ctk.CTkFrame(error_dialog, fg_color="#d32f2f", height=60)
#         header.pack(fill="x")
#         header.pack_propagate(False)
        
#         ctk.CTkLabel(
#             header,
#             text="⚠️ Error",
#             font=("Arial", 18, "bold"),
#             text_color="white"
#         ).pack(pady=15)
        
#         # Message
#         ctk.CTkLabel(
#             error_dialog,
#             text=message,
#             font=("Arial", 13),
#             wraplength=350,
#             justify="center"
#         ).pack(pady=20)
        
#         # OK button
#         ctk.CTkButton(
#             error_dialog,
#             text="OK",
#             width=100,
#             height=35,
#             fg_color="#d32f2f",
#             hover_color="#b71c1c",
#             command=error_dialog.destroy
#         ).pack(pady=10)
    
#     def show_success(self, message):
#         """Show success message"""
#         success_dialog = ctk.CTkToplevel(self)
#         success_dialog.title("Sukses")
#         success_dialog.geometry("400x220")
#         success_dialog.resizable(False, False)
#         success_dialog.configure(fg_color="#2a2a2a")
        
#         # Center
#         success_dialog.update_idletasks()
#         x = (success_dialog.winfo_screenwidth() // 2) - 200
#         y = (success_dialog.winfo_screenheight() // 2) - 110
#         success_dialog.geometry(f"400x220+{x}+{y}")
        
#         success_dialog.transient(self)
#         success_dialog.grab_set()
        
#         # Header
#         header = ctk.CTkFrame(success_dialog, fg_color="#4caf50", height=60)
#         header.pack(fill="x")
#         header.pack_propagate(False)
        
#         ctk.CTkLabel(
#             header,
#             text="✓ Sukses",
#             font=("Arial", 18, "bold"),
#             text_color="white"
#         ).pack(pady=15)
        
#         # Message
#         ctk.CTkLabel(
#             success_dialog,
#             text=message,
#             font=("Arial", 13),
#             wraplength=350,
#             justify="center"
#         ).pack(pady=20)
        
#         # OK button
#         ctk.CTkButton(
#             success_dialog,
#             text="OK",
#             width=100,
#             height=35,
#             fg_color="#4caf50",
#             hover_color="#45a049",
#             command=success_dialog.destroy
#         ).pack(pady=10)
#         if not re.match(pattern, tanggal_str):
#             return (False, "Format tanggal harus DD-MM-YYYY!", None)
        
#         try:
#             # Parse tanggal
#             day, month, year = tanggal_str.split('-')
#             day, month, year = int(day), int(month), int(year)
            
#             # Validate ranges
#             if year < 2000 or year > 2100:
#                 return (False, "Tahun harus antara 2000-2100!", None)
            
#             if month < 1 or month > 12:
#                 return (False, "Bulan harus antara 01-12!", None)
            
#             if day < 1 or day > 31:
#                 return (False, "Tanggal harus antara 01-31!", None)
            
#             # Validate dengan datetime (akan error jika tanggal tidak valid)
#             date_obj = datetime(year, month, day)
            
#             # Format ke YYYY-MM-DD untuk database
#             formatted_date = date_obj.strftime("%Y-%m-%d")
            
#             return (True, None, formatted_date)
            
#         except ValueError as e:
#             return (False, f"Tanggal tidak valid!\n{str(e)}", None)
    
#     def save_sertifikasi(self):
#         """Validate and save sertifikasi"""
#         from services.database import DB_Save_Sertifikasi
#         import uuid
        
#         # Get values
#         sertifikasi = self.sertifikasi_entry.get().strip()
#         year = self.year_entry.get().strip()
#         month = self.month_combo.get()
#         day = self.day_combo.get()
        
#         # Validation
#         if not sertifikasi:
#             self.show_error("Jenis sertifikasi tidak boleh kosong!")
#             self.sertifikasi_entry.focus()
#             return
        
#         # Validate date
#         try:
#             year_int = int(year)
#             if year_int < 2000 or year_int > 2100:
#                 raise ValueError("Tahun tidak valid")
            
#             tanggal_pelatihan = f"{year}-{month}-{day}"
#             # Validate date format
#             datetime.strptime(tanggal_pelatihan, "%Y-%m-%d")
            
#         except ValueError as e:
#             self.show_error(f"Tanggal tidak valid!\n{str(e)}")
#             return
        
#         # Generate unique ID
#         id_sertifikasi = f"SERT-{uuid.uuid4().hex[:8].upper()}"
        
#         try:
#             # Save to database
#             DB_Save_Sertifikasi(
#                 id_sertifikasi=id_sertifikasi,
#                 sertifikasi=sertifikasi,
#                 tanggal=tanggal_pelatihan
#             )
            
#             # Show success
#             self.show_success(
#                 f"✓ Sertifikasi berhasil ditambahkan!\n\n"
#                 f"ID: {id_sertifikasi}\n"
#                 f"Jenis: {sertifikasi}\n"
#                 f"Tanggal: {tanggal_pelatihan}"
#             )
            
#             # Callback to parent
#             if self.callback:
#                 self.callback()
            
#             # Close dialog
#             self.destroy()
            
#         except Exception as e:
#             self.show_error(f"Gagal menyimpan data!\n\n{str(e)}")
    
#     def show_error(self, message):
#         """Show error message"""
#         error_dialog = ctk.CTkToplevel(self)
#         error_dialog.title("Error")
#         error_dialog.geometry("400x200")
#         error_dialog.resizable(False, False)
#         error_dialog.configure(fg_color="#2a2a2a")
        
#         # Center
#         error_dialog.update_idletasks()
#         x = (error_dialog.winfo_screenwidth() // 2) - 200
#         y = (error_dialog.winfo_screenheight() // 2) - 100
#         error_dialog.geometry(f"400x200+{x}+{y}")
        
#         error_dialog.transient(self)
#         error_dialog.grab_set()
        
#         # Header
#         header = ctk.CTkFrame(error_dialog, fg_color="#d32f2f", height=60)
#         header.pack(fill="x")
#         header.pack_propagate(False)
        
#         ctk.CTkLabel(
#             header,
#             text="⚠️ Error",
#             font=("Arial", 18, "bold"),
#             text_color="white"
#         ).pack(pady=15)
        
#         # Message
#         ctk.CTkLabel(
#             error_dialog,
#             text=message,
#             font=("Arial", 13),
#             wraplength=350,
#             justify="center"
#         ).pack(pady=20)
        
#         # OK button
#         ctk.CTkButton(
#             error_dialog,
#             text="OK",
#             width=100,
#             height=35,
#             fg_color="#d32f2f",
#             hover_color="#b71c1c",
#             command=error_dialog.destroy
#         ).pack(pady=10)
    
#     def show_success(self, message):
#         """Show success message"""
#         success_dialog = ctk.CTkToplevel(self)
#         success_dialog.title("Sukses")
#         success_dialog.geometry("400x220")
#         success_dialog.resizable(False, False)
#         success_dialog.configure(fg_color="#2a2a2a")
        
#         # Center
#         success_dialog.update_idletasks()
#         x = (success_dialog.winfo_screenwidth() // 2) - 200
#         y = (success_dialog.winfo_screenheight() // 2) - 110
#         success_dialog.geometry(f"400x220+{x}+{y}")
        
#         success_dialog.transient(self)
#         success_dialog.grab_set()
        
#         # Header
#         header = ctk.CTkFrame(success_dialog, fg_color="#4caf50", height=60)
#         header.pack(fill="x")
#         header.pack_propagate(False)
        
#         ctk.CTkLabel(
#             header,
#             text="✓ Sukses",
#             font=("Arial", 18, "bold"),
#             text_color="white"
#         ).pack(pady=15)
        
#         # Message
#         ctk.CTkLabel(
#             success_dialog,
#             text=message,
#             font=("Arial", 13),
#             wraplength=350,
#             justify="center"
#         ).pack(pady=20)
        
#         # OK button
#         ctk.CTkButton(
#             success_dialog,
#             text="OK",
#             width=100,
#             height=35,
#             fg_color="#4caf50",
#             hover_color="#45a049",
#             command=success_dialog.destroy
#         ).pack(pady=10)