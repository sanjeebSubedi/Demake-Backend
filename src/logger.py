import logging
import os
from logging.handlers import RotatingFileHandler

if not os.path.exists("logs"):
    os.makedirs("logs")

log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

file_handler = RotatingFileHandler("logs/app.log", maxBytes=1_000_000, backupCount=5)
file_handler.setFormatter(log_formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

logger = logging.getLogger("twitter_demake_logger")
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def get_logger():
    return logger
