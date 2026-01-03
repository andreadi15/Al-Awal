    # services/export_excel.py
from openpyxl import Workbook
from pages.peserta_model import PesertaModel

class exportExcel():
    
    def __init__(self):
        self.KOTA_LIST = [
            # Sumatra
            "Banda Aceh", "Langsa", "Lhokseumawe", "Meulaboh", "Sabang", "Subulussalam", 
            "Binjai", "Gunungsitoli", "Medan", "Padangsidimpuan", "Pematangsiantar", 
            "Sibolga", "Tanjungbalai", "Tebing Tinggi", "Bukittinggi", "Padang", 
            "Padang Panjang", "Pariaman", "Payakumbuh", "Sawahlunto", "Solok", 
            "Dumai", "Pekanbaru", "Batam", "Tanjungpinang", "Jambi", "Sungaipenuh", 
            "Bengkulu", "Lubuklinggau", "Pagar Alam", "Palembang", "Prabumulih", 
            "Pangkalpinang", "Bandar Lampung", "Metro",

            # Jawa
            "Tangerang", "Tangerang Selatan", "Cilegon", "Serang", "Jakarta Pusat", 
            "Jakarta Barat", "Jakarta Timur", "Jakarta Utara", "Jakarta Selatan", 
            "Bandung", "Bekasi", "Bogor", "Cimahi", "Cirebon", "Depok", "Sukabumi", 
            "Tasikmalaya", "Banjar", "Magelang", "Pekalongan", "Salatiga", "Semarang", 
            "Surakarta", "Tegal", "Batu", "Blitar", "Kediri", "Madiun", "Malang", 
            "Mojokerto", "Pasuruan", "Probolinggo", "Surabaya", "Yogyakarta",

            # Kalimantan
            "Pontianak", "Singkawang", "Banjarbaru", "Banjarmasin", "Palangka Raya", 
            "Balikpapan", "Bontang", "Samarinda", "Nusantara", "Tarakan",

            # Sulawesi
            "Bitung", "Kotamobagu", "Manado", "Tomohon", "Palu", "Makassar", "Palopo", 
            "Parepare", "Baubau", "Kendari", "Gorontalo",

            # Bali & Nusa Tenggara
            "Denpasar", "Bima", "Mataram", "Kupang",

            # Maluku & Papua
            "Ambon", "Tual", "Ternate", "Tidore Kepulauan", "Jayapura", "Sorong"
        ]
                
    def export_peserta_to_excel(self,peserta_list, file_path):
        wb = Workbook()
        ws = wb.active
        ws.title = "Data Peserta"

        # Header
        headers = [
            "No",
            "Nama",
            "Skema",
            "NIK",
            "Tempat/Tanggal Lahir",
            "Alamat",
            "No. Telepon",
            "Pendidikan",
            "Instansi"
            "KTP",
            "Ijazah",
            "Pas Foto Merah",
            "CV",
            "TTD"
        ]

        ws.append(headers)

        # Data
        for i, p in enumerate(peserta_list, start=1):
            ws.append([
                i,
                p.nama,
                p.skema,
                p.nik,
                self.format_tempat_tanggal(p.tempat_lahir, p.tanggal_lahir),
                self.format_alamat(p),
                self.format_telepon(p.telepon),
                p.pendidikan,
                p.instansi,
                "TIDAK ADA",
                "TIDAK ADA",
                "TIDAK ADA",
                "TIDAK ADA",
                "TIDAK ADA"
            ])

        # Auto width (opsional tapi cakep)
        for col in ws.columns:
            max_len = max(len(str(cell.value)) if cell.value else 0 for cell in col)
            ws.column_dimensions[col[0].column_letter].width = max_len + 2

        wb.save(file_path)


    def format_tempat_tanggal(self,tempat, tanggal):
        if not tempat and not tanggal:
            return ""
        return f"{tempat}, {tanggal}"


    def format_alamat(self,p: PesertaModel):
        prefix = "KOTA" if p.kabupaten.lower() in self.KOTA_LIST else "KAB."

        return (
            f"{p.alamat}, "
            f"KEL. {p.kelurahan}, "
            f"KEC. {p.kecamatan}, "
            f"{prefix.upper()} {p.kabupaten}, "
            f"{p.provinsi}"
        )


    def format_telepon(self, nomor: str):
        nomor = nomor.replace("-", "").replace(" ", "")
        return "-".join(nomor[i:i+4] for i in range(0, len(nomor), 4))