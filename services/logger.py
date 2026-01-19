import logging, os
from datetime import datetime
from zoneinfo import ZoneInfo
from config import BASE_DIR

class AppLogger:
    _initialized = False

    @classmethod
    def setup(cls):
        if cls._initialized:
            return

        class WIBFormatter(logging.Formatter):
            def formatTime(self, record, datefmt=None):
                dt = datetime.fromtimestamp(
                    record.created,
                    ZoneInfo("Asia/Jakarta")
                )
                return dt.strftime(datefmt or "%Y-%m-%d %H:%M:%S")

        LOG_DIR = os.path.join(BASE_DIR, "logs")
        os.makedirs(LOG_DIR, exist_ok=True)

        log_file = os.path.join(
            LOG_DIR,
            f"App.log"
        )
        
        handler = logging.FileHandler(
            log_file,
            mode="a",          
            encoding="utf-8"
        )

        formatter = WIBFormatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )

        handler.setFormatter(formatter)

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(handler)

        cls._initialized = True
