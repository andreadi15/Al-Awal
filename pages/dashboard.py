# =======================
# FILE: pages/dashboard.py
# =======================
import customtkinter as ctk


class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=25, pady=25)
        
        ctk.CTkLabel(
            scroll,
            text="Dashboard",
            font=("Arial", 36, "bold")
        ).pack(anchor="w", pady=(0, 10))
        
        ctk.CTkLabel(
            scroll,
            text="Welcome to your workspace",
            font=("Arial", 14),
            text_color="#888888"
        ).pack(anchor="w", pady=(0, 30))
        
        stats_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))
        
        for i, (title, value, color) in enumerate([
            ("Total Projects", "24", "#1a73e8"),
            ("Active Tasks", "18", "#34a853"),
            ("Completed", "142", "#fbbc04")
        ]):
            card = ctk.CTkFrame(stats_frame, fg_color=color, corner_radius=12)
            card.grid(row=0, column=i, padx=10, pady=5, sticky="ew")
            stats_frame.grid_columnconfigure(i, weight=1)
            
            ctk.CTkLabel(card, text=value, font=("Arial", 32, "bold")).pack(pady=(20, 5))
            ctk.CTkLabel(card, text=title, font=("Arial", 13)).pack(pady=(0, 20))
        
        for i in range(5):
            card = ctk.CTkFrame(scroll, fg_color="#333333", corner_radius=12, height=120)
            card.pack(fill="x", pady=8)
            card.pack_propagate(False)
            
            content_inner = ctk.CTkFrame(card, fg_color="transparent")
            content_inner.pack(fill="both", expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(
                content_inner,
                text=f"Content Card #{i+1}",
                font=("Arial", 16, "bold"),
                anchor="w"
            ).pack(anchor="w")
            
            ctk.CTkLabel(
                content_inner,
                text="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                font=("Arial", 12),
                text_color="#888888",
                anchor="w"
            ).pack(anchor="w", pady=(5, 0))