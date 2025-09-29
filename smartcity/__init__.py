import logging
import os
import sys

# --- Versioning ---
__major__ = 0
__minor__ = 3
__release__ = 2
__pre_release__ = ".logs-supabase"
__version__ = f"{__major__}.{__minor__}.{__release__}{__pre_release__}"
__author__ = "Issa KAB"


# --- Logging for the project ---

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOG_DIR, "smartcity.log")

def _configure_base_logger(name="smartcity"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        file_handler = logging.FileHandler(LOG_FILE_PATH, mode="w", encoding="utf-8")
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s - %(funcName)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    logger.propagate = False
    return logger


logger = _configure_base_logger()