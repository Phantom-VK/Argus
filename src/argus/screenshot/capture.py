from src.argus.filemanager.file_manager import file_manager
from src.argus.logger import logging
import os
import random
import sys
from datetime import datetime
import mss

from src.argus.exceptions import CustomException
from src.argus.mousetracking.clicktracker import ClickTracker
from src.argus.timetracker.time_tracker import TimeTracker


class ScreenshotCapture:
    def __init__(self, clicktracker:ClickTracker):
        self.is_running = False
        self.is_paused = False
        self.user_id = ""
        self.screenshot_dir = ""
        self.click_tracker = clicktracker
        self.file_manager = file_manager
        self.time_tracker = TimeTracker()

    def start(self, user_id: str):
        self.user_id = user_id
        self.screenshot_dir = self.file_manager.get_screenshot_path(self.user_id)

        self.is_running = True
        self.is_paused = False
        logging.info("Tracking started")
        self.time_tracker.start()
        self.click_tracker.start_monitoring()

    def pause(self):
        self.is_paused = True
        self.time_tracker.pause()
        logging.info("Tracking paused")

    def resume(self):
        if self.is_running:
            self.is_paused = False
            self.time_tracker.start()
            logging.info("Tracking resumed")

    def stop(self):
        self.is_running = False
        logging.info("App stopped!")
        logging.info(f"Total work hours: {self.get_work_hours()}")
        self.click_tracker.stop_monitoring()



    def get_random_interval(self) -> int:
        return random.randint(120, 240)  # 2-4 minutes

    def capture(self) -> str:
        if not self.is_running or self.is_paused:
            return ""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(self.screenshot_dir, filename)

        try:
            with mss.mss() as sct:
                sct.shot(output=filepath)
                logging.info(f"Screenshot captured! Path: {filepath}")
            return filepath
        except Exception as e:
            raise CustomException(e, sys)

    def get_work_hours(self) -> str:
        return self.time_tracker.get_formatted_time()