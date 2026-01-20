# components/form_row.py
import customtkinter as ctk
from components.nik_entry import NikEntry

class createEntry:
    def __init__(self, parent, input_type, **kwargs):
        self.DEFAULT_BORDER_COLOR = "#1a73e8"  
        self.ERROR_BORDER_COLOR   = "#ff4d4f" 
       
        if input_type == "entry":
            self.widget = ctk.CTkEntry(
                parent,
                font=("Arial", 13),
                height=40,
                corner_radius=8,
                placeholder_text=kwargs.get("placeholder", ""),
                fg_color="#2a2a2a",
                border_color=self.DEFAULT_BORDER_COLOR,
            )
            
        elif input_type == "combobox":
            self.widget = ctk.CTkComboBox(
                parent,
                font=("Arial", 13),
                height=40,
                corner_radius=8,
                values=kwargs.get("options", []),
                fg_color="#2a2a2a",
                border_color=self.DEFAULT_BORDER_COLOR,
                button_color="#1a73e8",
                button_hover_color="#1557b0",
                dropdown_fg_color="#333333",
            )
            
            if "width" in kwargs:
                self.widget.configure(width=kwargs.get("width"))
                            
        elif input_type == "textbox":
            self.widget = ctk.CTkTextbox(
                parent,
                font=("Arial", 13),
                height=80,
                corner_radius=8,
                fg_color="#2a2a2a",
                border_color=self.DEFAULT_BORDER_COLOR,
                border_width=2 
            )
            
            placeholder = kwargs.get("placeholder", "")
            if placeholder:
                self.widget._placeholder_text = placeholder
                self.widget._placeholder_active = True
                
                self.widget.insert("1.0", placeholder)
                self.widget.configure(text_color="#8B8B8B")
                
                def on_focus_in_textbox(event):
                    if self.widget._placeholder_active and self.widget.get("1.0", "end-1c") == placeholder:
                        self.widget.delete("1.0", "end")
                        self.widget.configure(text_color="#cccccc")
                        self.widget._placeholder_active = False
                
                def on_focus_out_textbox(event):
                    content = self.widget.get("1.0", "end-1c").strip()
                    if not content:
                        self.widget.delete("1.0", "end")
                        self.widget.insert("1.0", placeholder)
                        self.widget.configure(text_color="#8B8B8B")
                        self.widget._placeholder_active = True
                    else:
                        self.widget.configure(text_color="#cccccc")
                        self.widget._placeholder_active = False
                
                self.widget.bind("<FocusIn>", on_focus_in_textbox)
                self.widget.bind("<FocusOut>", on_focus_out_textbox)
        elif input_type == "nik":
            self.widget = NikEntry(
                parent,
                font=("Arial", 13),
                height=40,
                corner_radius=8,
                placeholder_text=kwargs.get("placeholder", ""),
                fg_color="#2a2a2a",
                border_color=self.DEFAULT_BORDER_COLOR
            )
        else:
            raise ValueError(f"Unknown input_type: {input_type}")
        
        self.error_label = ctk.CTkLabel(
            parent,
            text="",
            font=("Arial", 11, "italic"),
            text_color="#ff6b6b",
            anchor="w",
        )

        self.widget.error_label = self.error_label

        # ======================
        # HANDLE ERROR API
        # ======================
        def set_error(message: str):
            """Kasih error ke field ini: border merah + teks di bawah input."""
            try:
                self.widget.configure(border_color=self.ERROR_BORDER_COLOR)
            except Exception:
                pass                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
            self.widget.error_label.configure(text=message)
            
        def clear_error():
            """Hilangkan error: border biru lagi + teks dikosongkan."""
            try:
                self.widget.configure(border_color=self.DEFAULT_BORDER_COLOR)
            except Exception:
                pass
            self.widget.error_label.configure(text="")

        self.widget.set_error = set_error
        self.widget.clear_error = clear_error

        # ======================
        # FOCUS EVENT HANDLER
        # ======================
        def on_focus_in(event):
            self.widget.clear_error()

        self.widget.bind("<FocusIn>", on_focus_in)

