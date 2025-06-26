import logging
import os
from datetime import datetime

from src.argus.filemanager.file_manager import file_manager

log_dir = file_manager.get_path("logs")
LOG_FILE_PATH = os.path.join(log_dir, f"logs_{datetime.now().strftime('%Y-%m-%d')}.log")

logging.basicConfig(
        handlers=[
            logging.FileHandler(LOG_FILE_PATH),
            logging.StreamHandler()
        ],
        format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO

)
