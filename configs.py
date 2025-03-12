import logging
from pathlib import Path
from constants import (BACKUP_COUNT, DATETIME_FORMAT, LOG_DIR, LOG_FILE,
                       LOG_FORMAT, MAX_BYTES_FOR_LOG_FILE)

from logging.handlers import RotatingFileHandler


def configure_logging():
    """Настройка конфигурации для логгирования."""
    log_dir = Path(LOG_DIR)
    log_dir.mkdir(exist_ok=True)
    rotating_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=MAX_BYTES_FOR_LOG_FILE, backupCount=BACKUP_COUNT
    )
    logging.basicConfig(
        datefmt=DATETIME_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler())
    )
