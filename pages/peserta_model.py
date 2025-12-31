# =======================
# FILE: models/peserta_model.py
# =======================

class PesertaModel:
    """
    Model untuk data peserta
    Menyimpan semua informasi peserta dalam satu object
    """
    
    def __init__(self, sertifikasi, skema, nama, nik, tempat_lahir, tanggal_lahir, 
                 alamat, kelurahan, kecamatan, kabupaten, provinsi, 
                 telepon, pendidikan, instansi):
        self.sertifikasi = sertifikasi
        self.skema = skema
        self.nama = nama
        self.nik = nik
        self.tempat_lahir = tempat_lahir
        self.tanggal_lahir = tanggal_lahir
        self.alamat = alamat
        self.kelurahan = kelurahan
        self.kecamatan = kecamatan
        self.kabupaten = kabupaten
        self.provinsi = provinsi
        self.telepon = telepon
        self.pendidikan = pendidikan
        self.instansi = instansi
    
    def to_dict(self):
        """Convert model ke dictionary untuk mudah disimpan"""
        return {
            "sertifikasi": self.sertifikasi,
            "skema": self.skema,
            "nama": self.nama,
            "nik": self.nik,
            "tempat_lahir": self.tempat_lahir,
            "tanggal_lahir": self.tanggal_lahir,
            "alamat": self.alamat,
            "kelurahan": self.kelurahan,
            "kecamatan": self.kecamatan,
            "kabupaten": self.kabupaten,
            "provinsi": self.provinsi,
            "telepon": self.telepon,
            "pendidikan": self.pendidikan,
            "instansi": self.instansi
        }
    
    @classmethod
    def from_dict(cls, data):
        """Buat PesertaModel dari dictionary"""
        return cls(
            sertifikasi=data.get("sertifikasi", ""),
            skema=data.get("skema", ""),
            nama=data.get("nama", ""),
            nik=data.get("nik", ""),
            tempat_lahir=data.get("tempat_lahir", ""),
            tanggal_lahir=data.get("tanggal_lahir", ""),
            alamat=data.get("alamat", ""),
            kelurahan=data.get("kelurahan", ""),
            kecamatan=data.get("kecamatan", ""),
            kabupaten=data.get("kabupaten", ""),
            provinsi=data.get("provinsi", ""),
            telepon=data.get("telepon", ""),
            pendidikan=data.get("pendidikan", ""),
            instansi=data.get("instansi", "")
        )
    
    def __str__(self):
        """String representation untuk debugging"""
        return f"PesertaModel(nama={self.nama}, nik={self.nik})"
    
    def __repr__(self):
        return self.__str__()