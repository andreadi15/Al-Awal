
import re
from pages.peserta_model import PesertaModel
# services/peserta_validator.py
"""Validasi form peserta saat ini"""

class PesertaValidator:
    @staticmethod
    def validate(peserta: PesertaModel):
        errors = {}
        
        # Validasi Nama
        if not peserta.nama.strip():
            errors["nama"] = "Nama lengkap harus diisi"
            
        # Validasi NIK (harus 16 digit)
        if len(peserta.nik) != 16 and len(peserta.nik) != 0:
            errors["nik"] = "NIK harus 16 digit"  
        
        # Validasi Tanggal Lahir
        tanggal = peserta.tanggal_lahir.strip()
        if not re.match(r'^\d{2}-\d{2}-\d{4}$', tanggal) and len(tanggal) != 0:
            errors["tanggal_lahir"] = "Format tanggal lahir: DD-MM-YYYY" 
        
        # Validasi No. Telepon
        telepon = peserta.telepon.strip()
        if not telepon.isdigit() and len(telepon) != 0:
            errors["telepon"] = "No. telepon harus berupa angka" 
            
        return errors
