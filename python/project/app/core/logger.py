import logging
import os
from app.core.config import settings

os.makedirs("logs", exist_ok=True)

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)

    if not logger.handlers:
        file_handler = logging.FileHandler("logs/app.log")
        console_handler = logging.StreamHandler()

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger