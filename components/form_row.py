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
        label.grid(row=row, column=0, sticky="w", pady=12, padx=(0, 20))

        widget.grid(
            row=row,
            column=1,
            sticky="ew",
            pady=12
        )

        parent.grid_columnconfigure(1, weight=1)
        self.widget = widget
