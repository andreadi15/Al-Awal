import sqlite3
from config import DB_PATH, DEBUG
from datetime import datetime
from models.peserta_model import PesertaModel
from services.logic import format_tanggal,return_format_tanggal

# ====== [DB] Connection Handler ======== 
def get_connection():
    return sqlite3.connect(DB_PATH)

# ====== [DB] Creating Table Data ======= 
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sertifikasi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_sertifikasi TEXT NOT NULL UNIQUE,
            sertifikasi TEXT NOT NULL,
            tanggal_pelatihan DATE NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS peserta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_peserta TEXT NOT NULL UNIQUE,
            id_sertifikasi TEXT NOT NULL,
            skema TEXT NOT NULL,
            nama TEXT,
            nik TEXT,
            tempat_lahir TEXT,
            tanggal_lahir DATE,
            alamat TEXT,
            kelurahan TEXT,
            kecamatan TEXT,
            kabupaten TEXT,
            provinsi TEXT,
            telepon TEXT,
            pendidikan TEXT,
            instansi TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_sertifikasi) REFERENCES sertifikasi(id_sertifikasi)
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_peserta_id_sertifikasi 
        ON peserta(id_sertifikasi)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_peserta_nama 
        ON peserta(nama)
    """)
    
    conn.commit()
    conn.close()


    if DEBUG:
        print("[DB] Database initialized")

# ========== [START] Peserta ============= 

def DB_Save_Peserta(peserta: PesertaModel, id_sertifikasi: str):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        cursor.execute("""
            INSERT INTO peserta (
                id_peserta,
                id_sertifikasi,
                skema,
                nama,
                nik,
                tempat_lahir,
                tanggal_lahir,
                alamat,
                kelurahan,
                kecamatan,
                kabupaten,
                provinsi,
                telepon,
                pendidikan,
                instansi,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            peserta.id_peserta,              # id_peserta
            id_sertifikasi,           # RELASI KE SERTIFIKASI
            peserta.skema,
            peserta.nama,
            peserta.nik,
            peserta.tempat_lahir,
            format_tanggal(peserta.tanggal_lahir),
            peserta.alamat,
            peserta.kelurahan,
            peserta.kecamatan,
            peserta.kabupaten,
            peserta.provinsi,
            peserta.telepon,
            peserta.pendidikan,
            peserta.instansi,
            now
        ))

        conn.commit()
        if DEBUG:
            print(f"[DB] Peserta saved: {peserta.nama} -> Sertifikasi: {id_sertifikasi}")
    except Exception as e:
        print("[DB ERROR SAVE]", e)
        raise

    finally:
        conn.close()
        
# Tambahkan di services/database.py

def DB_Save_Peserta_Batch(peserta_list: list[PesertaModel], id_sertifikasi: str):
    """
    Simpan banyak peserta sekaligus (optimized)
    """
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        data_to_insert = []
        for peserta in peserta_list:
            data_to_insert.append((
                peserta.id_peserta,
                id_sertifikasi,
                peserta.skema,
                peserta.nama,
                peserta.nik,
                peserta.tempat_lahir,
                format_tanggal(peserta.tanggal_lahir),
                peserta.alamat,
                peserta.kelurahan,
                peserta.kecamatan,
                peserta.kabupaten,
                peserta.provinsi,
                peserta.telepon,
                peserta.pendidikan,
                peserta.instansi,
                now
            ))
        
        cursor.executemany("""
            INSERT INTO peserta (
                id_peserta, id_sertifikasi, skema, nama, nik,
                tempat_lahir, tanggal_lahir, alamat, kelurahan,
                kecamatan, kabupaten, provinsi, telepon,
                pendidikan, instansi, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data_to_insert)
        
        conn.commit()
        
        if DEBUG:
            print(f"[DB] Batch saved {len(peserta_list)} peserta -> Sertifikasi: {id_sertifikasi}")
        
        return len(peserta_list)
        
    except Exception as e:
        conn.rollback()
        print("[DB ERROR BATCH SAVE]", e)
        raise
    finally:
        conn.close()
        
def DB_Get_Peserta_By_Sertifikasi(id_sertifikasi: str):
    """
    FUNGSI KUNCI UNTUK LAZY LOADING
    Ambil peserta hanya untuk sertifikasi tertentu
    Dipanggil saat header sertifikasi diklik (expand)
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            id_peserta,
            id_sertifikasi,
            skema,
            nama,
            nik,
            tempat_lahir,
            tanggal_lahir,
            alamat,
            kelurahan,
            kecamatan,
            kabupaten,
            provinsi,
            telepon,
            pendidikan,
            instansi
        FROM peserta
        WHERE id_sertifikasi = ?
        ORDER BY nama ASC
    """, (id_sertifikasi,))

    rows = cursor.fetchall()
    conn.close()

    peserta_list = []
    for row in rows:
        peserta = PesertaModel(
            id_peserta = row[0],
            id_sertifikasi = row[1],
            skema = row[2],
            nama = row[3],
            nik = row[4],
            tempat_lahir = row[5],
            tanggal_lahir = return_format_tanggal(row[6]),
            alamat = row[7],
            kelurahan = row[8],
            kecamatan = row[9],
            kabupaten = row[10],
            provinsi = row[11],
            telepon = row[12],
            pendidikan = row[13],
            instansi = row[14]
        )
        peserta_list.append(peserta)
    
    if DEBUG:
        print(f"[DB] Loaded {len(peserta_list)} peserta for sertifikasi: {id_sertifikasi}")

    return peserta_list        

def DB_Get_Peserta_Count_By_Sertifikasi(id_sertifikasi: str) -> int:
    """
    Hitung jumlah peserta tanpa load data lengkap
    Untuk ditampilkan di header (X peserta)
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM peserta 
        WHERE id_sertifikasi = ?
    """, (id_sertifikasi,))

    count = cursor.fetchone()[0]
    conn.close()
    
    return count

def DB_Search_Peserta(search_text: str, id_sertifikasi: str = None):
    """
    Search peserta dengan optional filter sertifikasi
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    search_pattern = f"%{search_text}%"
    
    if id_sertifikasi:
        # Search dalam sertifikasi tertentu
        cursor.execute("""
            SELECT 
                id, id_peserta, id_sertifikasi, skema,
                nama, nik, tempat_lahir, tanggal_lahir, alamat,
                kelurahan, kecamatan, kabupaten, provinsi,
                telepon, pendidikan, instansi
            FROM peserta
            WHERE id_sertifikasi = ?
            AND (
                nama LIKE ? OR 
                nik LIKE ? OR 
                no_peserta LIKE ?
            )
            ORDER BY nama ASC
        """, (id_sertifikasi, search_pattern, search_pattern, search_pattern))
    else:
        # Search global
        cursor.execute("""
            SELECT 
                id, id_peserta, id_sertifikasi, skema,
                nama, nik, tempat_lahir, tanggal_lahir, alamat,
                kelurahan, kecamatan, kabupaten, provinsi,
                telepon, pendidikan, instansi
            FROM peserta
            WHERE 
                nama LIKE ? OR 
                nik LIKE ? OR 
                id_peserta LIKE ?
            ORDER BY nama ASC
        """, (search_pattern, search_pattern, search_pattern))

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            'id': row[0], 'id_peserta': row[1], 'id_sertifikasi': row[2], 'skema': row[3], 'nama': row[4],
            'nik': row[5], 'tempat_lahir': row[6], 'tanggal_lahir': return_format_tanggal(row[7]),
            'alamat': row[8], 'kelurahan': row[9], 'kecamatan': row[10],
            'kabupaten': row[11], 'provinsi': row[12], 'telepon': row[13],
            'pendidikan': row[14], 'instansi': row[15]
        }
        for row in rows
    ]

def DB_Delete_Peserta_By_Sertifikasi(id_sertifikasi):
    """Delete semua peserta dari sertifikasi tertentu"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            DELETE FROM peserta 
            WHERE id_sertifikasi = ?
        """, (id_sertifikasi,))
        
        deleted = cursor.rowcount
        conn.commit()
        
        print(f"[INFO] Deleted {deleted} peserta from sertifikasi {id_sertifikasi}")
        return deleted
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Failed to delete peserta: {e}")
        raise e
    finally:
        conn.close()
        
def DB_Delete_Peserta(id_peserta: str):
    """Hapus peserta berdasarkan NIK"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM peserta WHERE id_peserta = ?", (id_peserta,))
    deleted = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    if DEBUG and deleted:
        print(f"[DB] Peserta deleted: ID Peserta {id_peserta}")
    
    return deleted

def DB_Delete_Peserta_Batch(id_peserta_list: list):
    """Hapus banyak peserta sekaligus (optimized)"""
    if not id_peserta_list:
        return 0
    
    conn = get_connection()
    cursor = conn.cursor()
    
    placeholders = ','.join(['?'] * len(id_peserta_list))
    cursor.execute(f"DELETE FROM peserta WHERE id_peserta IN ({placeholders})", id_peserta_list)
    
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    if DEBUG:
        print(f"[DB] Batch deleted {deleted_count} peserta")
    
    return deleted_count

def DB_Get_Peserta_By_Id(id_peserta: str):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT 
                id_peserta,
                id_sertifikasi,
                skema,
                nama,
                nik,
                tempat_lahir,
                tanggal_lahir,
                alamat,
                kelurahan,
                kecamatan,
                kabupaten,
                provinsi,
                telepon,
                pendidikan,
                instansi
            FROM peserta
            WHERE id_peserta = ?
            LIMIT 1
        """, (id_peserta,))

        row = cursor.fetchone()

        if not row:
            return None

        peserta = PesertaModel(
            id_peserta=row[0],
            id_sertifikasi=row[1],
            skema=row[2],
            nama=row[3],
            nik=row[4],
            tempat_lahir=row[5],
            tanggal_lahir=return_format_tanggal(row[6]),
            alamat=row[7],
            kelurahan=row[8],
            kecamatan=row[9],
            kabupaten=row[10],
            provinsi=row[11],
            telepon=row[12],
            pendidikan=row[13],
            instansi=row[14]
        )

        if DEBUG:
            print(f"[DB] Loaded peserta: {id_peserta}")

        return peserta

    finally:
        conn.close()
    
     
# =========== [END] Peserta ============== 


# ====== [START] SERTIFIKASI ============= 

def DB_Save_Sertifikasi(id_sertifikasi: str, sertifikasi: str, tanggal: str):
    """Simpan data sertifikasi baru"""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        cursor.execute("""
            INSERT INTO sertifikasi (
                id_sertifikasi,
                sertifikasi,
                tanggal_pelatihan,
                created_at
            )
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id_sertifikasi) DO UPDATE SET
                sertifikasi = excluded.sertifikasi,
                tanggal_pelatihan = excluded.tanggal_pelatihan;
        """, (
            id_sertifikasi,
            sertifikasi,
            tanggal,
            now
        ))

        conn.commit()
        
        if DEBUG:
            print(f"[DB] Sertifikasi saved: {id_sertifikasi} - {sertifikasi}")

    except Exception as e:
        print("[DB ERROR SAVE SERTIFIKASI]", e)
        raise

    finally:
        conn.close()

def DB_Get_All_Sertifikasi():
    """
    LOAD HANYA DATA SERTIFIKASI (tanpa peserta)
    Ini yang dipanggil saat halaman pertama kali dibuka
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            s.id_sertifikasi,
            s.sertifikasi,
            s.tanggal_pelatihan,
            COUNT(p.id) as jumlah_peserta
        FROM sertifikasi s
        LEFT JOIN peserta p ON s.id_sertifikasi = p.id_sertifikasi
        GROUP BY s.id_sertifikasi
        ORDER BY s.tanggal_pelatihan DESC, s.created_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    data_list = []
    for row in rows:
        data_list.append({
            "id_sertifikasi": row[0],
            "sertifikasi": row[1],
            "tanggal_pelatihan": row[2],
            "jumlah_peserta": row[3]
        })
    
    if DEBUG:
        print(f"[DB] Loaded {len(data_list)} sertifikasi")

    return data_list

def DB_Get_Sertifikasi_By_ID(id_sertifikasi: str):
    """Ambil detail sertifikasi berdasarkan ID"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            id_sertifikasi,
            sertifikasi,
            tanggal_pelatihan
        FROM sertifikasi
        WHERE id_sertifikasi = ?
        
    """, (id_sertifikasi,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id_sertifikasi": row[0],
            "sertifikasi": row[1],
            "tanggal_pelatihan": return_format_tanggal(row[2])
        }
    return None

def DB_Update_Sertifikasi(id_sertifikasi: str, sertifikasi: str, tanggal_pelatihan: str):
    """Update data sertifikasi"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE sertifikasi SET
                sertifikasi = ?,
                tanggal_pelatihan = ?
            WHERE id_sertifikasi = ?
        """, (sertifikasi, tanggal_pelatihan, id_sertifikasi))

        conn.commit()
        updated = cursor.rowcount > 0
        
        if DEBUG and updated:
            print(f"[DB] Sertifikasi updated: {id_sertifikasi}")
        
        return updated

    except Exception as e:
        print("[DB ERROR UPDATE SERTIFIKASI]", e)
        raise

    finally:
        conn.close()

def DB_Delete_Sertifikasi(id_sertifikasi: str, delete_peserta: bool = True):
    """
    Hapus sertifikasi
    Jika delete_peserta=True, hapus juga semua peserta terkait
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        if delete_peserta:
            # Hapus peserta terkait dulu
            cursor.execute("DELETE FROM peserta WHERE id_sertifikasi = ?", (id_sertifikasi,))
            peserta_deleted = cursor.rowcount
        
        # Hapus sertifikasi
        cursor.execute("DELETE FROM sertifikasi WHERE id_sertifikasi = ?", (id_sertifikasi,))
        sertifikasi_deleted = cursor.rowcount > 0
        
        conn.commit()
        
        if DEBUG:
            print(f"[DB] Sertifikasi deleted: {id_sertifikasi}")
            if delete_peserta:
                print(f"[DB] Also deleted {peserta_deleted} peserta")
        
        return sertifikasi_deleted
        
    except Exception as e:
        print("[DB ERROR DELETE SERTIFIKASI]", e)
        conn.rollback()
        raise
    finally:
        conn.close()
        
# ======= [END] SERTIFIKASI ============== 
























# ====== [DB] Insert Variable =========== 
def DB_Save_Variable(content, access_code, file_id, now):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO variables (access_code, content, file_id, created_at) VALUES (?, ?, ?, ?)", (access_code, content, file_id, now))

    conn.commit()
    if DEBUG:
        print(f"[DB] Content: {content}")
        print(f"[DB] Variable saved: {access_code}")

    conn.close()

# ====== [DB] Insert Daily Schedule ===== 
def DB_Save_Daily_Schedule(access_code,content,file_id,now):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO daily_schedule (access_code, content, file_id, created_at) VALUES (?, ?, ?, ?)", (access_code, content, file_id, now))

    conn.commit()
    if DEBUG:
        print(f"[DB] Content: {content}")
        print(f"[DB] Variable saved: {access_code}")

    conn.close()
    return access_code
    
    
# ====== [DB] Insert Template =========== 
def DB_Save_Template(access_code,content,now):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO template (access_code, content, created_at) VALUES (?, ?, ?)", (access_code,content,now))

    conn.commit()
    if DEBUG:
        print(f"[DB] Content: {content}")
        print(f"[DB] Variable saved: {access_code}")

    conn.close()
    return access_code
    

# ====== [DB] Get List All Template ===== 
def DB_All_Get_Template():
    if DEBUG:
        print("[DB] Get All Template")
        
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT access_code FROM template")
    alls = cursor.fetchall()
    conn.close()
    return [row[0] for row in alls] if alls else []

# ====== [DB] Show Content Template =====
def DB_Get_Template(access_code: str):
    if DEBUG:
        print("[DB] Get Content Template")
        
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT content FROM template WHERE access_code = ?",(access_code,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return row[0]
    return ""
    
# ====== [DB] Delete Template ===========
def DB_Remove_Template(access_code) -> bool:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM template WHERE access_code = ?",(access_code,))

        conn.commit()
        if DEBUG:
            print(f"[DB] Template Removed")
        return cursor.rowcount > 0
    finally:
        conn.close()
  
    
# ====== [DB] Count Total Variable ======
def DB_Cek_Index_Variable() -> int:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM variables")
    total_data = int(cursor.fetchone()[0])
    conn.close()
    return total_data

# ====== [DB] Cek Variable Exist ========
def DB_Get_User(user_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT user_id, first_name, last_name, username, is_active FROM users WHERE user_id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "user_id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "username": row[3],
            "is_active": row[4]
        }
    return {}


# ====== [DB] Cek Variable Exist ========
def DB_Cek_Variable(access_code: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM variables WHERE access_code = ? LIMIT 1",
        (access_code,)
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return True  # sudah ada
    return False  # belum ada

# ====== [DB] Cek Daily_Schedule Exist ===
def DB_Cek_Daily_Schedule(access_code: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM daily_schedule WHERE access_code = ? LIMIT 1",
        (access_code,)
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return True  # sudah ada
    return False  # belum ada

# ====== [DB] Cek Template Exist ========
def DB_Cek_Template(access_code: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM template WHERE access_code = ? LIMIT 1",
        (access_code,)
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return True  # sudah ada
    return False  # belum ada

# ====== [DB] Get Daily Auto ============
def DB_Get_Daily_Schedule() -> str:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, content FROM daily_schedule ORDER BY id ASC LIMIT 1")
    row = cursor.fetchone()

    if not row:
        conn.close()
        return ""

    schedule_id, content = row
    cursor.execute("DELETE FROM daily_schedule WHERE id = ?",(schedule_id,))
    conn.commit()
    conn.close()

    return content



# ====== [DB] Get List All Schedule  ====
def DB_All_Get_Daily_Schedule():
    if DEBUG:
        print("[DB] Get All Daily Schedule")
        
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT access_code FROM daily_schedule")
    alls = cursor.fetchall()
    conn.close()
    return [row[0] for row in alls] if alls else []

# ====== [DB] Show Content Schedule =====
def DB_Show_Daily_Schedule(access_code: str):
    if DEBUG:
        print("[DB] Get Content Daily Schedule")
        
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT content, file_id FROM daily_schedule WHERE access_code = ?",(access_code,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "content": row[0],
            "file_id": row[1]
        }
    return {}

# ====== [DB] Get Variable ==============
def DB_Get_Content(access_code: str):
    if DEBUG:
        print("[DB] Get Content")
        
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT content, file_id FROM variables WHERE access_code = ? ",(access_code,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "content": row[0],
            "file_id": row[1]
        }
    return {}


# ====== [DB] Get All User ==============
def DB_Get_All_User():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id, is_active FROM users")
    rows = cursor.fetchall()
    conn.close()
    if rows:
        return [
            {
                "user_id": row[0],
                "is_active": row[1]
            }
            for row in rows
        ]
    return []

# ====== [DB] Delete Schedule Auto ======
def DB_Remove_Daily_Schedule(access_code) -> bool:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM daily_schedule WHERE access_code = ?",(access_code,))

        conn.commit()
        if DEBUG:
            print(f"[DB] Schedule Removed")
        return cursor.rowcount > 0
    finally:
        conn.close()
        
# ====== [DB] Backup To Json ============
def DB_Backup():
    conn = get_connection()    
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    backup = {}

    # USERS
    cursor.execute("""
        SELECT user_id, first_name, last_name, username, is_active, created_at
        FROM users
    """)
    backup["users"] = [dict(row) for row in cursor.fetchall()]

    # VARIABLES
    cursor.execute("""
        SELECT access_code,  content, file_id, created_at
        FROM variables
    """)
    backup["variables"] = [dict(row) for row in cursor.fetchall()]

    # DAILY SCHEDULE
    cursor.execute("""
        SELECT access_code, content, file_id, created_at
        FROM daily_schedule
    """)
    backup["daily_schedule"] = [dict(row) for row in cursor.fetchall()]

    # TEMPLATE
    cursor.execute("""
        SELECT access_code, content, created_at
        FROM template
    """)
    backup["template"] = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return backup





