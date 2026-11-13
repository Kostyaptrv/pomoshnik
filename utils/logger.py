"""Базовое логирование для приложения."""

import logging
import os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, f"app_{datetime.now().strftime('%Y%m%d')}.log")

# Настраиваем логгер
logger = logging.getLogger("pomoshnik")
logger.setLevel(logging.DEBUG)

# Файловый handler — всё в файл
file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8", mode="a")
file_handler.setLevel(logging.DEBUG)
file_format = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(file_format)

# Консольный handler — только warnings+
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
console_handler.setFormatter(file_format)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
