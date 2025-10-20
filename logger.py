import logging
import os
import sys
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(asctime)s] #%(levelname)-4s %(filename)s:'
                              '%(lineno)d - %(name)s - %(message)s')

use_file_logs = os.getenv('USE_FILE_LOGS', 'false').lower() == 'true'

if use_file_logs:
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_filename = os.path.join(log_dir, f"logger_{current_date}.log")

    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def cleanup_old_logs():
    import glob

    log_pattern = os.path.join(log_dir, "logger_*.log")
    log_files = glob.glob(log_pattern)

    if len(log_files) > 5:
        log_files.sort(key=os.path.getctime)
        oldest_file = log_files[0]

        try:
            os.remove(oldest_file)
            logger.warning(f"Удалён старый лог-файл: {oldest_file}")  # WARN -> WARNING для совместимости
        except Exception as e:
            logger.error(f"Ошибка при удалении лог-файла: {e}")


if use_file_logs:
    cleanup_old_logs()

