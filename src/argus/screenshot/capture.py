import os
import sys
from datetime import datetime, timedelta

import mss
import mss.tools

from src.argus.api.tracker import api_client
from src.argus.exceptions import CustomException
from src.argus.filemanager.file_manager import file_manager
from src.argus.logger import logging
from src.argus.mousetracking.clicktracker import ClickTracker
from src.argus.timetracker.time_tracker import TimeTracker


class ScreenshotCapture:
    def __init__(self, clicktracker: ClickTracker):
        self.is_running = False
        self.is_paused = False
        self.user_id = ""
        self.screenshot_dir = ""
        self.click_tracker = clicktracker
        self.click_tracker.is_paused = False
        self.file_manager = file_manager
        self.last_capture_time = None
        self.last_unpaused_time = None
        self.time_tracker = TimeTracker()

    def start(self, user_id: str):
        self.user_id = user_id
        self.screenshot_dir = self.file_manager.get_screenshot_path(self.user_id)

        self.is_running = True
        self.is_paused = False
        logging.info("Tracking started")
        self.time_tracker.start()
        self.last_unpaused_time = datetime.now()
        self.click_tracker.start_monitoring()

    def pause(self):
        self.is_paused = True
        self.click_tracker.is_paused = True
        self.time_tracker.pause()
        logging.info("Tracking paused")

    def resume(self):
        if self.is_running:
            self.is_paused = False
            self.click_tracker.is_paused = False
            self.time_tracker.start()
            self.last_unpaused_time = datetime.now()
            logging.info("Tracking resumed")

    def stop(self):
        self.is_running = False
        logging.info("App stopped!")
        logging.info(f"Total work hours: {self.get_work_hours()}")
        self.click_tracker.stop_monitoring()
        self.last_capture_time = None

    def capture(self) -> bool:
        if not self.is_running or self.is_paused:
            return False

        current_time = datetime.now()

        # Calculate active time since last capture (excluding paused periods)
        if self.last_capture_time is None:
            # First capture - use time since start/resume
            time_gap = (current_time - self.last_unpaused_time).total_seconds()
        else:
            time_gap = (current_time - self.last_capture_time -
                        self.time_tracker.get_paused_duration_since(self.last_capture_time)).total_seconds()

        # Update timestamps
        self.last_capture_time = current_time
        self.last_unpaused_time = current_time

        filename = f"screenshot_{current_time.strftime("%Y%m%d_%H%M%S")}.png"
        filepath = os.path.join(self.screenshot_dir, filename)

        try:
            with mss.mss() as sct:
                monitor_areas = [sct.monitors[i] for i in range(1, len(sct.monitors))]
                left = min(m["left"] for m in monitor_areas)
                top = min(m["top"] for m in monitor_areas)
                right = max(m["left"] + m["width"] for m in monitor_areas)
                bottom = max(m["top"] + m["height"] for m in monitor_areas)
                # Capture the entire virtual screen
                screenshot = sct.grab({
                    "left": left,
                    "top": top,
                    "width": right - left,
                    "height": bottom - top
                })
                mss.tools.to_png(screenshot.rgb, screenshot.size, output=filepath)
                logging.info(f"Screenshot captured! Path: {filepath}")

                # Prepare upload
                print("Time_gap: ", time_gap)
                success = api_client.upload_activity(
                    employee_id=self.user_id,
                    screenshot_path=filepath,
                    work_seconds=str(time_gap)
                )

            return success
        except Exception as e:
            raise CustomException(e, sys)

    def get_work_hours(self) -> str:
        return self.time_tracker.get_formatted_time()
