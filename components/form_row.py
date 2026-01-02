# components/form_row.py
import customtkinter as ctk

class FormRow:
    def __init__(self, parent, row, label_text, widget):
        # Label kiri
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
            pady=(8, 0),     # sedikit jarak atas
            padx=(0, 20)
        )

        # Input kanan
        widget.grid(
            row=row,
            column=1,
            sticky="ew",
            pady=(8, 0)
        )

        # Label error (kalau ada dari create_entry)
        if hasattr(widget, "error_label"):
            # di bawah input, kolom yang sama
            widget.error_label.grid(
                row=row + 1,
                column=1,
                sticky="w",
                pady=(0, 8)   # jarak ke field berikutnya
            )
            # teks awal kosong, jadi visualnya cuma jarak aja

        parent.grid_columnconfigure(1, weight=1)
        self.widget = widget
