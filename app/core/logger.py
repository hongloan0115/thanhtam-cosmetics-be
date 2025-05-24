# app/core/logger.py

import logging
from logging.handlers import RotatingFileHandler
import sys

def get_logger(name: str = __name__) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)

        # Handler ghi log vào file, tự động xoay file khi >5MB, giữ lại 3 file backup
        file_handler = RotatingFileHandler(
            "app.log",
            maxBytes=5*1024*1024,
            backupCount=3,
            encoding="utf-8"
        )
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Handler log ra console
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    return logger
