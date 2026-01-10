    # services/export_excel.py
from openpyxl import Workbook
from pages.peserta_model import PesertaModel
from services.logic import format_kabupaten

class export_Awl_Report(): 
                
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

    @staticmethod
    def format_tempat_tanggal(tempat, tanggal):
        if not tempat and not tanggal:
            return ""
        return f"{tempat}, {tanggal}"

    def format_telepon(self, nomor: str):
        nomor = nomor.replace("-", "").replace(" ", "")
        return "-".join(nomor[i:i+4] for i in range(0, len(nomor), 4))
    
    def format_alamat(self,p: PesertaModel):
        if not p.alamat or not p.kelurahan or not p.kecamatan or not p.kabupaten or not p.provinsi:
            return ""
        alamat = (
            f"{p.alamat}, "
            f"KEL. {p.kelurahan}, "
            f"KEC. {p.kecamatan}, "
            f"{format_kabupaten(p.kabupaten)}, "
            f"{p.provinsi}"
        )
            
        return alamat
    


