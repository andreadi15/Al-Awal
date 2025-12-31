# components/form_row.py
import customtkinter as ctk
from nik_entry import NikEntry

class createEntry:
    def __init__(self, parent, input_type, **kwargs):
        """Helper untuk membuat baris form"""
        # Input widget
        if input_type == "entry":
            widget = ctk.CTkEntry(
                parent,
                font=("Arial", 13),
                height=40,
                corner_radius=8,
                placeholder_text=kwargs.get("placeholder", ""),
                fg_color="#2a2a2a",
                border_color="#1a73e8"
            )
            
        elif input_type == "combobox":
            widget = ctk.CTkComboBox(
                parent,
                font=("Arial", 13),
                height=40,
                corner_radius=8,
                values=kwargs.get("options", []),
                fg_color="#2a2a2a",
                border_color="#1a73e8",
                button_color="#1a73e8",
                button_hover_color="#1557b0",
                dropdown_fg_color="#333333",
            )
            
            if "width" in kwargs:
                widget.configure(width=kwargs.get("width"))
                
                
        elif input_type == "textbox":
            widget = ctk.CTkTextbox(
                parent,
                font=("Arial", 13),
                height=80,
                corner_radius=8,
                fg_color="#2a2a2a",
                border_color="#1a73e8"
            )
        elif input_type == "nik":
            widget = NikEntry(
                parent,
                font=("Arial", 13),
                height=40,
                corner_radius=8,
                placeholder_text=kwargs.get("placeholder", ""),
                fg_color="#2a2a2a",
                border_color="#1a73e8"
            )
            
        # Configure column weight
        
        return widget
