# constants/options.py
from services.logic import load_config
import os
from tkinter import messagebox
import sys

SKEMA_OPTIONS = [
    "Skema A",
    "Skema B",
    "Skema C",
    "Skema D"
]

PENDIDIKAN_OPTIONS = [
    "SD",
    "SMP",
    "SMA/SMK",
    "D3",
    "S1",
    "S2",
    "S3"
]

SERTIFIKASI_OPTIONS = [
    "BNSP",
    "CEPU",
    "IADC"
]

if os.path.exists("config.txt"):
    CONFIG = load_config("config.txt")
else:
    messagebox.showinfo("Informasi","File Config Tidak Ditemukan...")
    sys.exit(0)

BASE_DIR = os.getcwd()
DB_PATH = "database/data.db"
DEBUG = True
EMAIL = CONFIG['general']['email']
NAMA_PERUSAHAAN = CONFIG['general']['nama_perusahaan']
LOKASI_PERUSAHAAN = CONFIG['general']['lokasi_perusahaan']
TEMPLATE_DOK_BNSP = CONFIG['template']
TEMPLATE_BASE = CONFIG['general']['template_base'].replace("/","\\")