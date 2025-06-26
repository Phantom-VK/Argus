import os
import random
from datetime import datetime
import mss

from project_config import PROJECT_ROOT
from src.argus.mousetracking.clicktracker import ClickTracker
from src.argus.timetracker.time_tracker import TimeTracker


class ScreenshotCapture:
    def __init__(self):
        self.is_running = False
        self.is_paused = False
        self.user_id = ""
        self.screenshot_dir = os.path.join(PROJECT_ROOT, "screenshots", self.user_id)
        self.click_tracker = ClickTracker(inactivity_threshold=1800)  # 30 mins
        self.click_tracker.callback = self._handle_inactivity
        self.time_tracker = TimeTracker()
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def start(self, user_id: str):
        self.user_id = user_id
        self.screenshot_dir = os.path.join("screenshots", self.user_id)
        os.makedirs(self.screenshot_dir, exist_ok=True)

        self.is_running = True
        self.is_paused = False
        self.time_tracker.start()
        self.click_tracker.start_monitoring()

    def pause(self):
        self.is_paused = True
        self.time_tracker.pause()

    def resume(self):
        if self.is_running:
            self.is_paused = False
            self.time_tracker.start()

    def stop(self):
        self.is_running = False
        self.click_tracker.stop_monitoring()

    def _handle_inactivity(self):
        """Pause when inactivity detected"""
        if self.is_running and not self.is_paused:
            self.pause()

    def get_random_interval(self) -> int:
        return random.randint(120, 240)  # 2-4 minutes

    def capture(self) -> str:
        if not self.is_running or self.is_paused:
            return ""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.user_id}_{timestamp}.png"
        filepath = os.path.join(self.screenshot_dir, filename)

        try:
            with mss.mss() as sct:
                sct.shot(output=filepath)
            return filepath
        except Exception as e:
            print(f"Capture failed: {e}")
            return ""

    def get_work_hours(self) -> str:
        return self.time_tracker.get_formatted_time()