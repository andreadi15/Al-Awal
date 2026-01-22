import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from config import BASE_DIR

LOG_FILE = os.path.join(BASE_DIR, "app.log")

class WIBFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, ZoneInfo("Asia/Jakarta"))
        return dt.strftime(datefmt or "%Y-%m-%d %H:%M:%S")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8"),
    ]
)

for h in logging.getLogger().handlers:
    if isinstance(h, logging.FileHandler):
        h.setFormatter(WIBFormatter("%(asctime)s | %(levelname)s | %(message)s"))
