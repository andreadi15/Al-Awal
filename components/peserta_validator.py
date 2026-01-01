
import re
from pages.peserta_model import PesertaModel
# services/peserta_validator.py
"""Validasi form peserta saat ini"""

class PesertaValidator:
    @staticmethod
    def validate(peserta: PesertaModel):
        errors = {}

        # Validasi Sertifikasi
        if not peserta.sertifikasi.strip():
            errors["sertifikasi"] = "Sertifikasi harus dipilih"
        
        # Validasi Skema
        if not peserta.skema.strip():
            errors["skema"] = "Skema harus dipilih"
        
        # Validasi Nama
        if not peserta.nama.strip():
            errors["nama"] = "Nama lengkap harus diisi"
        
        # Validasi NIK (harus 16 digit)
        if len(peserta.nik) != 16:
            errors["nik"] = "NIK harus 16 digit" 
        
        # Validasi Tempat Lahir
        if not peserta.tempat_lahir.strip():
            errors["tempat_lahir"] = "Tempat lahir harus diisi" 
        
        # Validasi Tanggal Lahir
        tanggal = peserta.tanggal_lahir.strip()
        if not tanggal:
            errors["tanggal_lahir"] = "Tanggal lahir harus diisi" 
        elif not re.match(r'^\d{2}-\d{2}-\d{4}$', tanggal):
            errors["tanggal_lahir"] = "Format tanggal lahir: DD-MM-YYYY" 
        
        # Validasi Alamat
        if not peserta.alamat.strip():
            errors["alamat"] = "Alamat harus diisi" 
        
        # Validasi wilayah
        if not peserta.kelurahan.strip():
            errors["kelurahan"] = "Kelurahan harus diisi" 
        if not peserta.kecamatan.strip():
            errors["kecamatan"] = "Kecamatan harus diisi" 
        if not peserta.kabupaten.strip():
            errors["kabupaten"] = "Kabupaten harus diisi" 
        if not peserta.provinsi.strip():
            errors["provinsi"] = "Provinsi harus diisi" 
        
        # Validasi No. Telepon
        telepon = peserta.telepon.strip()
        if not telepon:
            errors["telepon"] = "No. telepon harus diisi" 
        elif not telepon.isdigit():
            errors["telepon"] = "No. telepon harus berupa angka" 
        
        # Validasi Pendidikan
        if not peserta.pendidikan.strip():
            errors["pendidikan"] = "Pendidikan terakhir harus dipilih" 
        
        # Validasi Instansi
        if not peserta.instansi.strip():
            errors["instansi"] = "Instansi harus diisi" 
            
        return errors
