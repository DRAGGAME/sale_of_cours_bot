import logging
import os
import glob
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(asctime)s] #%(levelname)-4s %(filename)s:'
                              '%(lineno)d - %(name)s - %(message)s')

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
current_date = datetime.now().strftime("%Y-%m-%d")
log_filename = os.path.join(log_dir, f"logger_{current_date}.log")

file_handler = logging.FileHandler(log_filename, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def cleanup_old_logs():
    log_pattern = os.path.join(log_dir, "logger_*.log")
    log_files = glob.glob(log_pattern)
    
    if len(log_files) > 5:
        log_files.sort(key=os.path.getctime)
        oldest_file = log_files[0]
        
        try:
            os.remove(oldest_file)
            logger.warn(f"Удалён старый лог-файл: {oldest_file}")
        except Exception as e:
            logger.error(f"Ошибка при удалении лог-файлфа: {e}")

cleanup_old_logs()