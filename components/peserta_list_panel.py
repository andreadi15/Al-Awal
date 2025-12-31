# components/peserta_list_panel.py
import customtkinter as ctk

class PesertaListPanel(ctk.CTkFrame):
    def __init__(self, parent, on_select, on_delete):
        super().__init__(parent)

        self.on_select = on_select
        self.on_delete = on_delete
        self.buttons = []

        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="x")

    def refresh(self, peserta_list, active_index):
        for b in self.buttons:
            b.destroy()
        self.buttons.clear()

        for i, p in enumerate(peserta_list):
            btn = ctk.CTkButton(
                self.container,
                text=f"Peserta {i+1}",
                fg_color="#3a3a3a" if i != active_index else "#1f6aa5",
                command=lambda idx=i: self.on_select(idx)
            )
            btn.pack(fill="x", pady=2)
            self.buttons.append(btn)
