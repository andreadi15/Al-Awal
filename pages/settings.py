# =======================
# FILE: pages/settings.py
# =======================
import customtkinter as ctk


class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Header
        ctk.CTkLabel(
            scroll,
            text="Settings",
            font=("Arial", 36, "bold")
        ).pack(anchor="w", pady=(0, 10))
        
        ctk.CTkLabel(
            scroll,
            text="Configure your application",
            font=("Arial", 14),
            text_color="#888888"
        ).pack(anchor="w", pady=(0, 30))
        
        # Settings sections
        sections = [
            ("Appearance", [
                ("Theme", ["Dark", "Light", "System"]),
                ("Accent Color", ["Blue", "Green", "Purple"]),
            ]),
            ("Notifications", [
                ("Email Notifications", None),
                ("Desktop Alerts", None),
            ]),
        ]
        
        for section_name, items in sections:
            section = ctk.CTkFrame(scroll, fg_color="#333333", corner_radius=12)
            section.pack(fill="x", pady=10)
            
            ctk.CTkLabel(
                section,
                text=section_name,
                font=("Arial", 18, "bold")
            ).pack(pady=(20, 10), padx=20, anchor="w")
            
            for label, options in items:
                item_frame = ctk.CTkFrame(section, fg_color="transparent")
                item_frame.pack(fill="x", padx=20, pady=10)
                
                ctk.CTkLabel(
                    item_frame,
                    text=label,
                    font=("Arial", 14)
                ).pack(side="left")
                
                if options:
                    menu = ctk.CTkOptionMenu(
                        item_frame,
                        values=options,
                        width=150
                    )
                    menu.pack(side="right")
                else:
                    switch = ctk.CTkSwitch(item_frame, text="")
                    switch.pack(side="right")
            
            ctk.CTkLabel(section, text="").pack(pady=10)  # Spacing