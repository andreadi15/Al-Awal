# =======================
# FILE: pages/projects.py
# =======================
import customtkinter as ctk


class ProjectsPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Header
        ctk.CTkLabel(
            scroll,
            text="Projects",
            font=("Arial", 36, "bold")
        ).pack(anchor="w", pady=(0, 10))
        
        ctk.CTkLabel(
            scroll,
            text="Manage your projects",
            font=("Arial", 14),
            text_color="#888888"
        ).pack(anchor="w", pady=(0, 30))
        
        # Project Grid
        projects_grid = ctk.CTkFrame(scroll, fg_color="transparent")
        projects_grid.pack(fill="both", expand=True)
        
        projects = [
            ("Website Redesign", "In Progress", "#1a73e8"),
            ("Mobile App", "Planning", "#fbbc04"),
            ("Marketing Campaign", "Completed", "#34a853"),
            ("Data Analysis", "In Progress", "#1a73e8"),
        ]
        
        for i, (name, status, color) in enumerate(projects):
            card = ctk.CTkFrame(projects_grid, fg_color="#333333", corner_radius=12)
            card.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
            projects_grid.grid_columnconfigure(0, weight=1)
            projects_grid.grid_columnconfigure(1, weight=1)
            
            ctk.CTkLabel(
                card,
                text=name,
                font=("Arial", 18, "bold")
            ).pack(pady=(20, 10), padx=20, anchor="w")
            
            status_badge = ctk.CTkFrame(card, fg_color=color, corner_radius=6)
            status_badge.pack(pady=(0, 20), padx=20, anchor="w")
            
            ctk.CTkLabel(
                status_badge,
                text=status,
                font=("Arial", 11),
                text_color="white"
            ).pack(padx=10, pady=5)