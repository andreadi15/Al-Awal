
import re
from models.peserta_model import PesertaModel

class PesertaValidator:
    @staticmethod
    def validate(peserta: PesertaModel):
        errors = {}
        
        if not peserta.nama.strip():
            errors["nama"] = "Nama lengkap harus diisi"
            
        if len(peserta.nik) != 16 and len(peserta.nik) != 0:
            errors["nik"] = "NIK harus 16 digit"  
        
        tanggal = peserta.tanggal_lahir.strip()
        if not re.match(r'^\d{2}-\d{2}-\d{4}$', tanggal) and len(tanggal) != 0:
            errors["tanggal_lahir"] = "Format tanggal lahir: DD-MM-YYYY" 
        
        telepon = peserta.telepon.strip()
        if not telepon.isdigit() and len(telepon) != 0:
            errors["telepon"] = "No. telepon harus berupa angka" 
            
        return errors
