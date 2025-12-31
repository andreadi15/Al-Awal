
import re
from pages.peserta_model import PesertaModel
# services/peserta_validator.py
"""Validasi form peserta saat ini"""

class PesertaValidator:
    @staticmethod
    def validate(peserta: PesertaModel):
        errors = []

        # Validasi Sertifikasi
        if not peserta.sertifikasi.get():
            errors.append("Sertifikasi harus dipilih")
        
        # Validasi Skema
        if not peserta.skema.get():
            errors.append("Skema harus dipilih")
        
        # Validasi Nama
        if not peserta.nama.get().strip():
            errors.append("Nama lengkap harus diisi")
        
        # Validasi NIK (harus 16 digit)
        if len(peserta.nik) != 16:
            errors.append("NIK harus 16 digit")
        
        # Validasi Tempat Lahir
        if not peserta.tempat_lahir.get().strip():
            errors.append("Tempat lahir harus diisi")
        
        # Validasi Tanggal Lahir
        tanggal = peserta.tanggal_lahir.get().strip()
        if not tanggal:
            errors.append("Tanggal lahir harus diisi")
        elif not re.match(r'^\d{2}-\d{2}-\d{4}$', tanggal):
            errors.append("Format tanggal lahir: DD-MM-YYYY")
        
        # Validasi Alamat
        if not peserta.alamat.get("1.0", "end").strip():
            errors.append("Alamat harus diisi")
        
        # Validasi wilayah
        if not peserta.kelurahan.get().strip():
            errors.append("Kelurahan harus diisi")
        if not peserta.kecamatan.get().strip():
            errors.append("Kecamatan harus diisi")
        if not peserta.kabupaten.get().strip():
            errors.append("Kabupaten harus diisi")
        if not peserta.provinsi.get().strip():
            errors.append("Provinsi harus diisi")
        
        # Validasi No. Telepon
        telepon = peserta.telepon.get().strip()
        if not telepon:
            errors.append("No. telepon harus diisi")
        elif not telepon.isdigit():
            errors.append("No. telepon harus berupa angka")
        
        # Validasi Pendidikan
        if not peserta.pendidikan.get():
            errors.append("Pendidikan terakhir harus dipilih")
        
        return errors
