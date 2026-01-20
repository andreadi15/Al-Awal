# constants/options.py
from services.logic import load_config
import os
from tkinter import messagebox
import sys

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

PDFCONVERTER_DPI = CONFIG['general']['pdfconverter_dpi']

TEMPLATE_DOK_BNSP = CONFIG['template']
TEMPLATE_BASE = CONFIG['general']['template_base'].replace("/","\\")
TEMPLATE_AWL_REPORT = CONFIG['general']['template_awl_report'].replace("/","\\")
TEMPLATE_REKAP_BNSP = CONFIG['general']['template_rekap_bnsp'].replace("/","\\")

PENDIDIKAN_OPTIONS = CONFIG['general']['pendidikan_option']
SERTIFIKASI_OPTIONS = CONFIG['general']['sertifikasi_option']