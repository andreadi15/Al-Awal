# components/form_row.py
import customtkinter as ctk

class FormRow:
    def __init__(self, parent, row, label_text, widget):
       
        label = ctk.CTkLabel(
            parent,
            text=label_text,
            font=("Arial", 14, "bold"),
            anchor="w",
            text_color="#ffffff"
        )
        label.bind("<Button-1>", lambda e: label.focus_set())

        label.grid(
            row=row,
            column=0,
            sticky="w",
            pady=(8, 0),     
            padx=(0, 20)
        )

        widget.grid(
            row=row,
            column=1,
            sticky="ew",
            pady=(8, 0)
        )

        if hasattr(widget, "error_label"):
            widget.error_label.grid(
                row=row + 1,
                column=1,
                sticky="w",
                pady=(0, 8)   
            )

        parent.grid_columnconfigure(1, weight=1)
        self.widget = widget
