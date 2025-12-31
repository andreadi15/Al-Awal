# =======================
# FILE: pages/peserta.py
# =======================
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta
import random

class PesertaPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#2a2a2a")
        
        # Data dummy
        self.all_data = self.generate_dummy_data()
        self.filtered_data = self.all_data.copy()
        self.selected_ids = set()
        
        # Settings
        self.rows_per_page = 10
        self.current_page = 1
        
        self.create_widgets()
        self.refresh_display()
    
    def generate_dummy_data(self):
        """Generate dummy data peserta"""
        data = []
        sertifikasi_types = ["BNSP", "CEPU", "IADC"]
        names = ["Ahmad", "Budi", "Citra", "Dewi", "Eko", "Farah", "Gilang", "Hana"]
        
        # Generate data untuk 3 tanggal berbeda
        base_date = datetime.now()
        for day_offset in range(3):
            date = (base_date - timedelta(days=day_offset)).strftime("%Y-%m-%d")
            
            # Random 5-15 peserta per tanggal
            num_peserta = random.randint(5, 15)
            for i in range(num_peserta):
                data.append({
                    'id': len(data) + 1,
                    'tanggal': date,
                    'nama': f"{random.choice(names)} {random.choice(['Santoso', 'Wijaya', 'Kusuma', 'Pratama'])}",
                    'sertifikasi': random.choice(sertifikasi_types),
                    'no_peserta': f"P{random.randint(1000, 9999)}",
                    'status': random.choice(['Lulus', 'Tidak Lulus', 'Proses'])
                })
        
        return data
    
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
        
        title = ctk.CTkLabel(
            header_frame,
            text="👥 Kelola Peserta",
            font=("Arial", 28, "bold"),
            text_color="#ffffff"
        )
        title.pack(side="left", pady=20)
    
    def create_controls(self):
        """Create search, filter, and pagination controls"""
        controls_frame = ctk.CTkFrame(self, fg_color="#1f1f1f", height=70)
        controls_frame.pack(fill="x", padx=20, pady=(0, 15))
        controls_frame.pack_propagate(False)
        
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
            placeholder_text="Nama peserta, no peserta..."
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", lambda e: self.apply_filters())
        
        # Middle: Date filter
        date_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        date_frame.pack(side="left", padx=15, pady=10)
        
        ctk.CTkLabel(
            date_frame,
            text="📅 Tanggal:",
            font=("Arial", 13)
        ).pack(side="left", padx=(0, 8))
        
        dates = ["Semua"] + sorted(list(set([d['tanggal'] for d in self.all_data])), reverse=True)
        self.date_combo = ctk.CTkComboBox(
            date_frame,
            values=dates,
            width=150,
            height=35,
            command=lambda x: self.apply_filters()
        )
        self.date_combo.set("Semua")
        self.date_combo.pack(side="left")
        
        # Right side: Rows per page
        rows_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        rows_frame.pack(side="right", padx=15, pady=10)
        
        ctk.CTkLabel(
            rows_frame,
            text="📊 Rows:",
            font=("Arial", 13)
        ).pack(side="left", padx=(0, 8))
        
        self.rows_combo = ctk.CTkComboBox(
            rows_frame,
            values=["5", "10", "20", "50"],
            width=80,
            height=35,
            command=self.change_rows_per_page
        )
        self.rows_combo.set(str(self.rows_per_page))
        self.rows_combo.pack(side="left")
    
    def create_tables_container(self):
        """Create scrollable container for tables"""
        # Container with scrollbar
        self.scroll_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.scroll_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Pagination info and controls
        self.pagination_frame = ctk.CTkFrame(self, fg_color="#1f1f1f", height=60)
        self.pagination_frame.pack(fill="x", padx=20, pady=(0, 20))
        self.pagination_frame.pack_propagate(False)
    
    def refresh_display(self):
        """Refresh all tables based on current filters and pagination"""
        # Clear existing tables
        for widget in self.scroll_container.winfo_children():
            widget.destroy()
        
        # Group data by date
        grouped_data = {}
        for item in self.filtered_data:
            date = item['tanggal']
            if date not in grouped_data:
                grouped_data[date] = []
            grouped_data[date].append(item)
        
        # Sort dates descending
        sorted_dates = sorted(grouped_data.keys(), reverse=True)
        
        # Pagination
        start_idx = (self.current_page - 1) * self.rows_per_page
        end_idx = start_idx + self.rows_per_page
        
        current_count = 0
        for date in sorted_dates:
            items = grouped_data[date]
            
            # Check if we need to show this date table
            items_in_range = []
            for item in items:
                if start_idx <= current_count < end_idx:
                    items_in_range.append(item)
                current_count += 1
            
            if items_in_range:
                self.create_date_table(date, items_in_range, len(items))
        
        # Update pagination
        self.update_pagination()
    
    def create_date_table(self, date, items, total_items):
        """Create collapsible table for a specific date"""
        # Main container
        table_container = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        table_container.pack(fill="x", pady=(0, 15))
        
        # Date header with collapse button
        header_frame = ctk.CTkFrame(table_container, fg_color="#1a73e8", height=50)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Collapse button
        collapse_var = ctk.BooleanVar(value=True)
        collapse_btn = ctk.CTkButton(
            header_frame,
            text="▼",
            width=40,
            height=40,
            fg_color="transparent",
            hover_color="#1557b0",
            font=("Arial", 16, "bold"),
            command=lambda: self.toggle_table(table_container, collapse_btn, collapse_var)
        )
        collapse_btn.pack(side="left", padx=10)
        
        # Date label
        date_label = ctk.CTkLabel(
            header_frame,
            text=f"📅 {date}",
            font=("Arial", 16, "bold"),
            text_color="white"
        )
        date_label.pack(side="left", padx=10)
        
        # Count label
        count_label = ctk.CTkLabel(
            header_frame,
            text=f"({len(items)} dari {total_items} peserta)",
            font=("Arial", 13),
            text_color="#e0e0e0"
        )
        count_label.pack(side="left", padx=5)
        
        # Table content frame
        content_frame = ctk.CTkFrame(table_container, fg_color="#1f1f1f")
        content_frame.pack(fill="x", pady=(2, 0))
        
        # Action panel (delete selected)
        self.create_action_panel(content_frame, date)
        
        # Table headers
        self.create_table_headers(content_frame)
        
        # Table rows
        for item in items:
            self.create_table_row(content_frame, item)
        
        # Store reference
        table_container._content_frame = content_frame
        table_container._collapse_var = collapse_var
    
    def create_action_panel(self, parent, date):
        """Create action panel with delete button"""
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
            command=self.delete_selected
        )
        delete_btn.pack(side="left", padx=15)
        
        # Selected count
        count_label = ctk.CTkLabel(
            panel,
            text=f"Terpilih: {len(self.selected_ids)} item",
            font=("Arial", 13, "bold"),
            text_color="white"
        )
        count_label.pack(side="left", padx=10)
        
        # Store reference for updating
        panel._count_label = count_label
        parent._action_panel = panel
    
    def create_table_headers(self, parent):
        """Create table column headers"""
        header_frame = ctk.CTkFrame(parent, fg_color="#333333", height=45)
        header_frame.pack(fill="x", padx=10, pady=(0, 2))
        header_frame.pack_propagate(False)
        
        # Configure grid
        header_frame.grid_columnconfigure(0, weight=0, minsize=50)  # Checkbox
        header_frame.grid_columnconfigure(1, weight=1, minsize=80)  # No
        header_frame.grid_columnconfigure(2, weight=3, minsize=200) # Nama
        header_frame.grid_columnconfigure(3, weight=2, minsize=120) # Sertifikasi
        header_frame.grid_columnconfigure(4, weight=2, minsize=120) # No Peserta
        header_frame.grid_columnconfigure(5, weight=2, minsize=120) # Status
        
        headers = ["☑", "No", "Nama Peserta", "Sertifikasi", "No. Peserta", "Status"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                header_frame,
                text=header,
                font=("Arial", 13, "bold"),
                text_color="#ffffff"
            )
            label.grid(row=0, column=i, padx=10, sticky="w")
    
    def create_table_row(self, parent, item):
        """Create a data row"""
        row_frame = ctk.CTkFrame(parent, fg_color="#2a2a2a", height=50)
        row_frame.pack(fill="x", padx=10, pady=1)
        row_frame.pack_propagate(False)
        
        # Configure grid
        row_frame.grid_columnconfigure(0, weight=0, minsize=50)
        row_frame.grid_columnconfigure(1, weight=1, minsize=80)
        row_frame.grid_columnconfigure(2, weight=3, minsize=200)
        row_frame.grid_columnconfigure(3, weight=2, minsize=120)
        row_frame.grid_columnconfigure(4, weight=2, minsize=120)
        row_frame.grid_columnconfigure(5, weight=2, minsize=120)
        
        # Checkbox
        check_var = ctk.BooleanVar(value=item['id'] in self.selected_ids)
        checkbox = ctk.CTkCheckBox(
            row_frame,
            text="",
            width=30,
            variable=check_var,
            command=lambda: self.toggle_selection(item['id'], check_var)
        )
        checkbox.grid(row=0, column=0, padx=15)
        
        # Data cells
        cells = [
            str(item['id']),
            item['nama'],
            item['sertifikasi'],
            item['no_peserta'],
            item['status']
        ]
        
        for i, cell in enumerate(cells, start=1):
            # Color code status
            text_color = "#ffffff"
            if i == 5:  # Status column
                if cell == "Lulus":
                    text_color = "#4caf50"
                elif cell == "Tidak Lulus":
                    text_color = "#f44336"
                else:
                    text_color = "#ff9800"
            
            label = ctk.CTkLabel(
                row_frame,
                text=cell,
                font=("Arial", 12),
                text_color=text_color,
                anchor="w"
            )
            label.grid(row=0, column=i, padx=10, sticky="w")
    
    def toggle_table(self, container, btn, var):
        """Toggle table visibility"""
        is_visible = var.get()
        
        if is_visible:
            # Hide
            container._content_frame.pack_forget()
            btn.configure(text="▶")
            var.set(False)
        else:
            # Show
            container._content_frame.pack(fill="x", pady=(2, 0))
            btn.configure(text="▼")
            var.set(True)
    
    def toggle_selection(self, item_id, var):
        """Toggle item selection"""
        if var.get():
            self.selected_ids.add(item_id)
        else:
            self.selected_ids.discard(item_id)
        
        # Update all action panels
        self.update_action_panels()
    
    def update_action_panels(self):
        """Update all action panel counts"""
        for widget in self.scroll_container.winfo_children():
            if hasattr(widget, '_content_frame'):
                content = widget._content_frame
                if hasattr(content, '_action_panel'):
                    panel = content._action_panel
                    if hasattr(panel, '_count_label'):
                        panel._count_label.configure(
                            text=f"Terpilih: {len(self.selected_ids)} item"
                        )
    
    def delete_selected(self):
        """Delete selected items"""
        if not self.selected_ids:
            messagebox.showinfo("Info", "Tidak ada item yang dipilih!")
            return
        
        result = messagebox.askyesno(
            "Konfirmasi",
            f"Hapus {len(self.selected_ids)} peserta terpilih?"
        )
        
        if result:
            # Remove from data
            self.all_data = [d for d in self.all_data if d['id'] not in self.selected_ids]
            self.filtered_data = [d for d in self.filtered_data if d['id'] not in self.selected_ids]
            
            # Clear selection
            self.selected_ids.clear()
            
            # Refresh
            self.current_page = 1
            self.refresh_display()
            
            messagebox.showinfo("Sukses", "Data berhasil dihapus!")
    
    def apply_filters(self):
        """Apply search and date filters"""
        search_text = self.search_entry.get().lower()
        date_filter = self.date_combo.get()
        
        # Filter data
        self.filtered_data = []
        for item in self.all_data:
            # Date filter
            if date_filter != "Semua" and item['tanggal'] != date_filter:
                continue
            
            # Search filter
            if search_text:
                searchable = f"{item['nama']} {item['no_peserta']} {item['sertifikasi']}".lower()
                if search_text not in searchable:
                    continue
            
            self.filtered_data.append(item)
        
        # Reset to page 1
        self.current_page = 1
        self.refresh_display()
    
    def change_rows_per_page(self, value):
        """Change rows per page"""
        self.rows_per_page = int(value)
        self.current_page = 1
        self.refresh_display()
    
    def update_pagination(self):
        """Update pagination controls"""
        # Clear existing
        for widget in self.pagination_frame.winfo_children():
            widget.destroy()
        
        total_items = len(self.filtered_data)
        total_pages = max(1, (total_items + self.rows_per_page - 1) // self.rows_per_page)
        
        # Info label
        start_item = (self.current_page - 1) * self.rows_per_page + 1
        end_item = min(self.current_page * self.rows_per_page, total_items)
        
        info_label = ctk.CTkLabel(
            self.pagination_frame,
            text=f"Menampilkan {start_item}-{end_item} dari {total_items} peserta | Halaman {self.current_page} dari {total_pages}",
            font=("Arial", 13)
        )
        info_label.pack(side="left", padx=20)
        
        # Navigation buttons
        nav_frame = ctk.CTkFrame(self.pagination_frame, fg_color="transparent")
        nav_frame.pack(side="right", padx=20)
        
        # Previous button
        prev_btn = ctk.CTkButton(
            nav_frame,
            text="◀ Prev",
            width=80,
            height=35,
            state="normal" if self.current_page > 1 else "disabled",
            command=self.prev_page
        )
        prev_btn.pack(side="left", padx=5)
        
        # Page numbers
        for page in range(max(1, self.current_page - 2), min(total_pages + 1, self.current_page + 3)):
            btn = ctk.CTkButton(
                nav_frame,
                text=str(page),
                width=40,
                height=35,
                fg_color="#1a73e8" if page == self.current_page else "#333333",
                command=lambda p=page: self.goto_page(p)
            )
            btn.pack(side="left", padx=2)
        
        # Next button
        next_btn = ctk.CTkButton(
            nav_frame,
            text="Next ▶",
            width=80,
            height=35,
            state="normal" if self.current_page < total_pages else "disabled",
            command=self.next_page
        )
        next_btn.pack(side="left", padx=5)
    
    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_display()
    
    def next_page(self):
        """Go to next page"""
        total_pages = max(1, (len(self.filtered_data) + self.rows_per_page - 1) // self.rows_per_page)
        if self.current_page < total_pages:
            self.current_page += 1
            self.refresh_display()
    
    def goto_page(self, page):
        """Go to specific page"""
        self.current_page = page
        self.refresh_display()