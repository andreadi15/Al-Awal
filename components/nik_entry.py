# components/nik_entry.py
import customtkinter as ctk

class NikEntry(ctk.CTkEntry):
    PLACEHOLDER = "─" * 16

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._value = ""
        self.insert(0, self._format())
        self.bind("<KeyPress>", self._on_key)

    def _format(self):
        full = self._value + self.PLACEHOLDER[len(self._value):]
        return " ".join(full[i:i+4] for i in range(0, 16, 4))

    def _on_key(self, event):
        if event.keysym == "Tab":
            return
    
        if event.keysym == "BackSpace":
            self._value = self._value[:-1]
        elif event.char.isdigit() and len(self._value) < 16:
            self._value += event.char
        else:
            return "break"

        self.delete(0, "end")
        self.insert(0, self._format())
        return "break"

    def get_value(self):
        return self._value
