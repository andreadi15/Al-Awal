from datetime import datetime

def format_tanggal(tanggal):
    """Convert berbagai format tanggal ke YYYY-MM-DD"""
    if not tanggal or not tanggal.strip():
        return None
    
    tanggal = tanggal.strip()
    
    # Try multiple formats
    formats = [
        "%d/%m/%Y",   # 17/12/2025
        "%d-%m-%Y",   # 17-12-2025
        "%Y-%m-%d",   # 2025-12-17 (already correct)
        "%Y/%m/%d",   # 2025/12/17
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(tanggal, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    return None
    
def return_format_tanggal(tanggal):
    """Convert berbagai format tanggal ke DD-MM-YYYY"""
    if not tanggal or not tanggal.strip():
        return None

    tanggal = tanggal.strip()

    formats = [
        "%Y-%m-%d",   # 2025-12-17
        "%Y/%m/%d",   # 2025/12/17
        "%d-%m-%Y",   # 17-12-2025 (already correct)
        "%d/%m/%Y",   # 17/12/2025
    ]

    for fmt in formats:
        try:
            return datetime.strptime(tanggal, fmt).strftime("%d-%m-%Y")
        except ValueError:
            continue

    return None

@staticmethod
def format_kabupaten(kabupaten: str):
    KOTA_LIST = [
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
    prefix = "KOTA" if kabupaten.lower() in KOTA_LIST else "KAB."
    return f"{prefix.upper()} {kabupaten}"
    