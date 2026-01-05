import customtkinter as ctk
from components.create_entry import createEntry
import re
from config import SERTIFIKASI_OPTIONS
from datetime import datetime 

# ============================================
# CUSTOM DIALOG: Tambah Sertifikasi
# ============================================

class AddSertifikasiDialog(ctk.CTkToplevel):
    """
    Custom dialog untuk menambah sertifikasi baru
    Matching dengan design main aplikasi
    Responsive dan auto-center di layar user
    """
    def __init__(self, parent, callback, sertif=None):
        super().__init__(parent)
    
        self.callback = callback
        
        self.id_sertifikasi = sertif["id_sertifikasi"] if sertif else None
        self.tanggal_pelatihan = datetime.strptime(sertif["tanggal_pelatihan"], "%Y-%m-%d").strftime("%d-%m-%Y") if sertif else None
        self.sertifikasi = sertif["sertifikasi"] if sertif else None
            
        # Window configuration
        self.title("Tambah Sertifikasi Baru")
        
        # Set size dulu (before centering)
        dialog_width = 500
        dialog_height = 450
        self.geometry(f"{dialog_width}x{dialog_height}")
        self.resizable(False, False)
        
        # CRITICAL: Update window untuk mendapatkan ukuran screen yang akurat
        self.update_idletasks()
        
        # Center window - Hitung posisi berdasarkan ukuran screen dan window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        x = ((screen_width - dialog_width) // 2) + 130
        y = ((screen_height - dialog_height) // 2) + 30
        
        # Set posisi ke center
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Style matching main app
        self.configure(fg_color="#2a2a2a")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create dialog content"""
        # Header
        header = ctk.CTkFrame(self, fg_color="#1a73e8", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="➕ Tambah Sertifikasi Baru",
            font=("Arial", 22, "bold"),
            text_color="white"
        ).pack(pady=25)
        
        # Content frame
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Form fields container
        form_frame = ctk.CTkFrame(content, fg_color="transparent")
        form_frame.pack(fill="x", side="top")
        
        # 1. Jenis Sertifikasi
        ctk.CTkLabel(
            form_frame,
            text="📜 Jenis Sertifikasi",
            font=("Arial", 14, "bold"),
            anchor="w"
        ).pack(fill="x", pady=(0, 8))
        
        self.sertifikasi_entry = ctk.CTkComboBox(
            form_frame,
            height=45,
            values=SERTIFIKASI_OPTIONS,
            font=("Arial", 14, "bold")
        )
        self.sertifikasi_entry.pack(fill="x", pady=(0, 20))
        if self.sertifikasi != None:
            self.sertifikasi_entry.set(self.sertifikasi)
        
        # 2. Tanggal Pelatihan
        ctk.CTkLabel(
            form_frame,
            text="📅 Tanggal Pelatihan",
            font=("Arial", 14, "bold"),
            anchor="w"
        ).pack(fill="x", pady=(0, 8))
        
        date_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        date_frame.pack(fill="x", pady=(0, 5))
        
        self.tanggal_entry = ctk.CTkEntry(
            date_frame,
            height=45,
            font=("Arial", 14),
            placeholder_text="DD-MM-YYYY"
        )
        self.tanggal_entry.pack(fill="x")
        
        # Bind KeyPress untuk format otomatis
        self.tanggal_entry.bind("<KeyPress>", self.format_tanggal_input)
        
        # Set default tanggal hari ini
        today = datetime.now()
        default_date = today.strftime("%d-%m-%Y")
        if self.tanggal_pelatihan == None:
            self.tanggal_entry.insert(0, default_date)
        else:
            self.tanggal_entry.insert(0, self.tanggal_pelatihan)
        
        
        # Buttons - Pack di bottom dengan side="bottom" SEBELUM spacer
        button_frame = ctk.CTkFrame(content, fg_color="transparent", height=60)
        button_frame.pack(side="bottom", fill="x", pady=(5, 0))
        button_frame.pack_propagate(False)
        
        # Configure grid untuk spacing yang sama
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        # Cancel button - Grid row 0, column 0
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="✕ Batal",
            height=50,  # Fixed height
            font=("Arial", 14, "bold"),
            fg_color="#757575",
            hover_color="#616161",
            corner_radius=10,
            command=self.destroy
        )
        cancel_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        # Save button - Grid row 0, column 1
        save_btn = ctk.CTkButton(
            button_frame,
            text="✓ Simpan",
            height=50,  # Fixed height
            font=("Arial", 14, "bold"),
            fg_color="#4caf50",
            hover_color="#45a049",
            corner_radius=10,
            command=self.save_sertifikasi
        )
        save_btn.grid(row=0, column=1, padx=(5, 0), sticky="ew")
        
        # Focus to first field
        self.sertifikasi_entry.focus()
    
    def format_tanggal_input(self, event):  # atau format_tanggal_lahir
        """Handler untuk input tanggal dengan format DD-MM-YYYY"""
        entry = event.widget
        current_text = entry.get()
        
        navigation_keys = ["Left", "Right", "Home", "End", "Up", "Down"]
        if event.keysym in navigation_keys:
            return
        
        # 🔥 SIMPAN posisi cursor SEBELUM modifikasi
        cursor_pos = entry.index("insert")
        
        # Ambil hanya digit dari text saat ini
        current_digits = re.sub(r'\D', '', current_text)
        
        # Handle Backspace
        if event.keysym == "BackSpace":
            if cursor_pos > 0:
                # Hitung posisi digit yang akan dihapus
                # Hitung berapa separator sebelum cursor
                separators_before = current_text[:cursor_pos].count('-')
                # Posisi digit = cursor - jumlah separator
                digit_pos = cursor_pos - separators_before - 1
                
                if digit_pos >= 0 and digit_pos < len(current_digits):
                    # Hapus digit di posisi yang benar
                    current_digits = current_digits[:digit_pos] + current_digits[digit_pos + 1:]
            else:
                return "break"
                
        # Handle input digit
        elif event.char.isdigit():
            if len(current_digits) >= 8:
                return "break"
            
            # Hitung posisi digit untuk insert
            separators_before = current_text[:cursor_pos].count('-')
            digit_pos = cursor_pos - separators_before
            
            # Insert digit di posisi yang benar
            current_digits = current_digits[:digit_pos] + event.char + current_digits[digit_pos:]
            
        else:
            # Block karakter selain digit atau backspace
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
        
        # 🔥 RESTORE posisi cursor dengan adjustment
        if event.keysym == "BackSpace":
            # Setelah backspace, cursor mundur 1 posisi
            new_cursor_pos = max(0, cursor_pos - 1)
            # Skip separator jika cursor di atasnya
            if new_cursor_pos > 0 and new_cursor_pos < len(formatted) and formatted[new_cursor_pos] == '-':
                new_cursor_pos -= 1
        else:
            # Setelah insert digit, cursor maju 1 posisi
            new_cursor_pos = cursor_pos + 1
            # Skip separator jika auto-inserted
            if new_cursor_pos < len(formatted) and formatted[new_cursor_pos] == '-':
                new_cursor_pos += 1
        
        # Set cursor position
        entry.icursor(min(new_cursor_pos, len(formatted)))
        
        return "break"
    
    def validate_tanggal(self, tanggal_str):
        """
        Validate tanggal format DD-MM-YYYY
        Return tuple: (is_valid, error_message, formatted_date)
        """
        if not tanggal_str or tanggal_str.strip() == "":
            return (False, "Tanggal tidak boleh kosong!", None)
        
        # Cek format dengan regex
        pattern = r'^\d{2}-\d{2}-\d{4}$'
        
        if not re.match(pattern, tanggal_str):
            return (False, "Format tanggal harus DD-MM-YYYY!", None)
        
        try:
            # Parse tanggal
            day, month, year = tanggal_str.split('-')
            day, month, year = int(day), int(month), int(year)
            
            # Validate ranges
            if year < 2000 or year > 2100:
                return (False, "Tahun harus antara 2000-2100!", None)
            
            if month < 1 or month > 12:
                return (False, "Bulan harus antara 01-12!", None)
            
            if day < 1 or day > 31:
                return (False, "Tanggal harus antara 01-31!", None)
            
            # Validate dengan datetime (akan error jika tanggal tidak valid)
            date_obj = datetime(year, month, day)
            
            # Format ke YYYY-MM-DD untuk database
            formatted_date = date_obj.strftime("%Y-%m-%d")
            
            return (True, None, formatted_date)
            
        except ValueError as e:
            return (False, f"Tanggal tidak valid!\n{str(e)}", None)
    
    def save_sertifikasi(self):
        """Validate and save sertifikasi"""
        from services.database import DB_Save_Sertifikasi
        import uuid
        
        # Get values
        sertifikasi = self.sertifikasi_entry.get().strip()
        tanggal_input = self.tanggal_entry.get().strip()
        
        # Validation: Jenis Sertifikasi
        if not sertifikasi:
            self.show_error("Jenis sertifikasi tidak boleh kosong!")
            self.sertifikasi_entry.focus()
            return
        
        # Validation: Tanggal
        is_valid, error_msg, tanggal_pelatihan = self.validate_tanggal(tanggal_input)
        if not is_valid:
            self.show_error(error_msg)
            self.tanggal_entry.focus()
            return
        
        # Generate unique ID
        if not self.id_sertifikasi:
            self.id_sertifikasi = f"SERT-{uuid.uuid4().hex[:8].upper()}"
        
        try:
            # Save to database
            DB_Save_Sertifikasi(
                id_sertifikasi=self.id_sertifikasi,
                sertifikasi=sertifikasi,
                tanggal=tanggal_pelatihan  # Format: YYYY-MM-DD
            )
            
            # Format tanggal untuk display (DD-MM-YYYY)
            # display_date = datetime.strptime(tanggal_pelatihan, "%Y-%m-%d").strftime("%d-%m-%Y")
            
            # # Show success
            # self.show_success(
            #     f"✓ Sertifikasi berhasil ditambahkan!\n\n"
            #     f"ID: {self.id_sertifikasi}\n"
            #     f"Jenis: {sertifikasi}\n"
            #     f"Tanggal: {display_date}"
            # )
            
            # Close dialog
            self.destroy()
            
            # Callback to parent
            if self.callback:
                self.after(100, self.callback)
            
        except Exception as e:
            self.show_error(f"Gagal menyimpan data!\n\n{str(e)}")
    
    def show_error(self, message):
        """Show error message with auto-center"""
        error_dialog = ctk.CTkToplevel(self)
        error_dialog.title("Error")
        
        # Set size
        dialog_width = 400
        dialog_height = 200
        error_dialog.geometry(f"{dialog_width}x{dialog_height}")
        error_dialog.resizable(False, False)
        error_dialog.configure(fg_color="#2a2a2a")
        
        # CRITICAL: Update untuk mendapatkan ukuran screen
        error_dialog.update_idletasks()
        
        # Center relative to screen
        screen_width = error_dialog.winfo_screenwidth()
        screen_height = error_dialog.winfo_screenheight()
        
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        
        error_dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        error_dialog.transient(self)
        error_dialog.grab_set()
        
        # Header
        header = ctk.CTkFrame(error_dialog, fg_color="#d32f2f", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="⚠️ Error",
            font=("Arial", 18, "bold"),
            text_color="white"
        ).pack(pady=15)
        
        # Message
        ctk.CTkLabel(
            error_dialog,
            text=message,
            font=("Arial", 13),
            wraplength=350,
            justify="center"
        ).pack(pady=20)
        
        # OK button
        ctk.CTkButton(
            error_dialog,
            text="OK",
            width=120,
            height=40,
            font=("Arial", 14, "bold"),
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            corner_radius=10,
            command=error_dialog.destroy
        ).pack(pady=10)
    
    # def show_success(self, message):
    #     """Show success message with auto-center"""
    #     success_dialog = ctk.CTkToplevel(self)
    #     success_dialog.title("Sukses")
        
    #     # Set size
    #     dialog_width = 400
    #     dialog_height = 240
    #     success_dialog.geometry(f"{dialog_width}x{dialog_height}")
    #     success_dialog.resizable(False, False)
    #     success_dialog.configure(fg_color="#2a2a2a")
        
    #     # CRITICAL: Update untuk mendapatkan ukuran screen
    #     success_dialog.update_idletasks()
        
    #     # Center relative to screen
    #     screen_width = success_dialog.winfo_screenwidth()
    #     screen_height = success_dialog.winfo_screenheight()
        
    #     x = (screen_width - dialog_width) // 2
    #     y = (screen_height - dialog_height) // 2
        
    #     success_dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
    #     success_dialog.transient(self)
    #     success_dialog.grab_set()
        
    #     # Header
    #     header = ctk.CTkFrame(success_dialog, fg_color="#4caf50", height=60)
    #     header.pack(fill="x")
    #     header.pack_propagate(False)
        
    #     ctk.CTkLabel(
    #         header,
    #         text="✓ Sukses",
    #         font=("Arial", 18, "bold"),
    #         text_color="white"
    #     ).pack(pady=15)
        
    #     # Message
    #     ctk.CTkLabel(
    #         success_dialog,
    #         text=message,
    #         font=("Arial", 13),
    #         wraplength=350,
    #         justify="center"
    #     ).pack(pady=20)
        
    #     # OK button
    #     ctk.CTkButton(
    #         success_dialog,
    #         text="OK",
    #         width=120,
    #         height=40,
    #         font=("Arial", 14, "bold"),
    #         fg_color="#4caf50",
    #         hover_color="#45a049",
    #         corner_radius=10,
    #         command=success_dialog.destroy
    #     ).pack(pady=10)
        
        