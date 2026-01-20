# =======================
# FILE: main.py
# =======================
import customtkinter as ctk
from pages.dashboard import DashboardPage
from pages.peserta import PesertaPage
from pages.inputpeserta import InputPesertaPage
from pages.pdf2image import Pdf2ImagePage 
from pages.projects import ProjectsPage
from pages.settings import SettingsPage
from services.database import init_db
import logging
from services.logger import LOG_FILE

class App(ctk.CTk):
    NAV_WIDTH = 220
    TOGGLE_BTN_SIZE = 45
    BTN_MARGIN = 30

    def __init__(self):
        super().__init__()
            
        ctk.set_appearance_mode("dark")

        self.title("APP KU")
        self.after(10, lambda: self.state("zoomed"))
        self.configure(fg_color="gray")

        self.nav_visible = True
        self.current_page = None

        # Konfigurasi grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0, minsize=self.NAV_WIDTH)
        self.grid_columnconfigure(1, weight=1)

        self.create_nav()
        self.create_content_container()
        self.create_toggle_button()
        
        # Load halaman default
        self.show_page("Dashboard")

    def create_nav(self):
        self.nav = ctk.CTkFrame(self, width=self.NAV_WIDTH, fg_color="#1f1f1f")
        self.nav.grid(row=0, column=0, sticky="nsew")
        self.nav.grid_propagate(False)
        self.nav.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(
            self.nav, 
            fg_color="transparent", 
            height=self.BTN_MARGIN + self.TOGGLE_BTN_SIZE + 10
        )
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)

        title = ctk.CTkLabel(
            header,
            text="📱 APP KU",
            font=("Arial", 18, "bold")
        )
        title.pack(side="left", padx=15, pady=self.BTN_MARGIN)

        # Menu items container
        menu_frame = ctk.CTkFrame(self.nav, fg_color="transparent")
        menu_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        self.menu_items = [
            ("🏠", "Dashboard"),
            ("👥", "Peserta"),
            ("➕", "Input Peserta"),
            ("📄", "PDF2Image"),
            ("📊", "Projects"),
            ("⚙️", "Settings"),
        ]
        
        self.menu_buttons = {}
        
        for icon, item in self.menu_items:
            btn_widget = self.create_menu_button(menu_frame, icon, item)
            self.menu_buttons[item] = btn_widget

    def create_menu_button(self, parent, icon, text):
        """
        Menu button dengan proper sizing:
        - Container 80% dari NAV_WIDTH
        - Button full width tanpa padding
        """
        # Hitung 80% dari nav width untuk container
        container_width = int(self.NAV_WIDTH * 0.8)
        
        # Container dengan fixed width 80%
        container = ctk.CTkFrame(parent, fg_color="#333333", width=container_width, height=50)
        container.pack(pady=3, anchor="w")  # anchor="w" biar rata kiri
        container.pack_propagate(False)  # PENTING: jaga fixed width
        
        # Button TANPA padx - langsung full!
        btn = ctk.CTkButton(
            container,
            text=f"{icon}  {text}",
            fg_color="#CF0404",
            hover=False,
            corner_radius=8,
            height=50,
            anchor="w",
            font=("Arial", 15),
            command=lambda: self.show_page(text)
        )
        btn.pack(fill="both", expand=True)  # TANPA padx!
        
        # Store state
        btn._page_name = text
        btn._is_hovered = False
        
        # Hover events
        def on_enter(e):
            btn._is_hovered = True
            btn.configure(fg_color="#B8B8B8", text_color="#333333")
        
        def on_leave(e):
            btn._is_hovered = False
            if self.current_page != text:
                btn.configure(fg_color="#333333",text_color="#ffffff")
        
        # Bind hover
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn

    def create_content_container(self):
        """Container untuk content yang bisa diganti-ganti"""
        self.content_container = ctk.CTkFrame(self, fg_color="#2a2a2a")
        self.content_container.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

    def show_page(self, page_name, id_sertifikasi=None):
        """
        Ganti halaman yang ditampilkan dengan auto-save state
        """
        # Save current page state before switching
        if self.current_page:
            # Get current page widget
            for widget in self.content_container.winfo_children():
                if hasattr(widget, 'save_state'):
                    try:
                        widget.save_state()
                        print(f"[APP] Saved state for: {self.current_page}")
                    except Exception as e:
                        print(f"[APP] Error saving state: {e}")
                break
        
        # Destroy current page
        if self.current_page:
            for widget in self.content_container.winfo_children():
                widget.destroy()
        
        # Update menu highlights - reset semua button dulu
        for name, btn in self.menu_buttons.items():
            if name == page_name:
                # Button yang diklik: tetap di hover color
                btn.configure(fg_color="#B8B8B8", text_color="#333333")
            else:
                # Button lain: kembalikan ke transparent
                if not getattr(btn, '_is_hovered', False):
                    btn.configure(fg_color="transparent", text_color="#ffffff")
        
        # Load new page
        if page_name == "Dashboard":
            page = DashboardPage(self.content_container)
        elif page_name == "Peserta":
            page = PesertaPage(self.content_container, self)
        elif page_name == "Input Peserta":
            page = InputPesertaPage(self.content_container, id_sertifikasi)
        elif page_name == "PDF2Image": 
            page = Pdf2ImagePage(self.content_container)
            if hasattr(page, 'restore_state'):
                page.restore_state()
        elif page_name == "Projects":
            page = ProjectsPage(self.content_container)
        elif page_name == "Settings":
            page = SettingsPage(self.content_container)
        else:
            page = DashboardPage(self.content_container)
        
        page.pack(fill="both", expand=True)
        self.current_page = page_name

    def create_toggle_button(self):
        """Buat tombol toggle"""
        self.toggle_btn = ctk.CTkButton(
            self,
            text="✕",
            width=self.TOGGLE_BTN_SIZE,
            height=self.TOGGLE_BTN_SIZE,
            corner_radius=10,
            fg_color="#1a73e8",
            hover_color="#1557b0",
            font=("Arial", 22, "bold"),
            command=self.toggle_nav,
            border_width=0,
            border_spacing=0,
            text_color="white"
        )
        
        self.update_toggle_position()

    def update_toggle_position(self):
        """Update posisi dan icon tombol"""
        if self.nav_visible:
            x = self.NAV_WIDTH - self.TOGGLE_BTN_SIZE - 15
            y = self.BTN_MARGIN
            icon = "✕"
        else:
            x = -(self.TOGGLE_BTN_SIZE // 2)
            y = self.BTN_MARGIN
            icon = "☰"
        
        self.toggle_btn.configure(text=icon)
        self.toggle_btn.place(x=x, y=y)

    def toggle_nav(self):
        """Toggle nav dengan manipulasi width only"""
        if self.nav_visible:
            target_width = 0
            target_minsize = 0
            new_content_padx = (0, 0)
        else:
            target_width = self.NAV_WIDTH
            target_minsize = self.NAV_WIDTH
            new_content_padx = (5, 0)
        
        self.nav.configure(width=target_width)
        self.grid_columnconfigure(0, minsize=target_minsize)
        self.content_container.grid_configure(padx=new_content_padx)
        
        self.nav_visible = not self.nav_visible
        self.update_toggle_position()
        
        self.update_idletasks()

if __name__ == "__main__":
    # logging.info("[Logger] Logging Initiate")
    init_db()
    app = App()
    app.mainloop()
    
    
    
    
    
    
    
    
    
# diclaude tambahin update ketika user input 1 peserta maka tombolnya simpan hanya "Simpan",tapi ketika klik tombol selanjutnya maka tombol simpan ganti textnya dengan "Simpan Semua",dan ketika tombol selanjutnya ditekan dan data terakhir tidak diisi dengan lengkap maka 
# udahlah bikin aja sebuah kolom khusus untuk menyimpan data ketika tombol selanjutnyaditekan maka create data dikolom itu gitu