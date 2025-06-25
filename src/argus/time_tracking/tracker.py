import threading
import time
from datetime import datetime, timedelta
from typing import Optional

from src.argus.screenshot.capture import capture_screenshot

TIME_FORMAT = "%H_%M_%S"


class TimeTracker:
    def __init__(self):
        self.start_time: Optional[datetime] = None
        self.total_paused_time = timedelta()
        self.last_pause_time: Optional[datetime] = None
        self.is_paused = False
        self.capture_thread: Optional[threading.Thread] = None
        self.stop_capture = False

    def calc_work_hours(self) -> str:
        """Calculate worked hours accounting for pauses"""
        if not self.start_time:
            return "00:00:00"

        current_time = datetime.now()

        if self.is_paused and self.last_pause_time:
            # Time while paused doesn't count toward work hours
            self.total_paused_time += current_time - self.last_pause_time

        total_worked = current_time - self.start_time - self.total_paused_time
        hours, remainder = divmod(total_worked.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def start_tracking(self):
        """Start the work session timer"""
        if not self.start_time:
            self.start_time = datetime.now()
            print(f"Work session started at {self.start_time.strftime(TIME_FORMAT)}")

    def pause_tracking(self):
        """Pause the work session timer"""
        if not self.is_paused:
            self.last_pause_time = datetime.now()
            self.is_paused = True
            print("Work session paused")

    def resume_tracking(self):
        """Resume the work session timer"""
        if self.is_paused and self.last_pause_time:
            self.total_paused_time += datetime.now() - self.last_pause_time
            self.is_paused = False
            print("Work session resumed")

    def _capture_screenshot(self):
        """Internal method to capture screenshots"""
        capture_screenshot()

    def _capture_loop(self, gap: int):
        """Continuous screenshot capture"""
        while not self.stop_capture:
            self._capture_screenshot()
            time.sleep(gap * 60)  # Convert minutes to seconds

    def start_capturing(self, gap: int = 5):
        """Start periodic screenshot capture"""
        if not self.capture_thread or not self.capture_thread.is_alive():
            self.stop_capture = False
            self.capture_thread = threading.Thread(
                target=self._capture_loop,
                args=(gap,),
                daemon=True
            )
            self.capture_thread.start()
            print(f"Started capturing screenshots every {gap} minutes")

    def stop_capturing(self):
        """Stop periodic screenshot capture"""
        if self.capture_thread and self.capture_thread.is_alive():
            self.stop_capture = True
            self.capture_thread.join()
            print("Stopped screenshot capture")


if __name__ == "__main__":
    tracker = TimeTracker()

    # Example usage
    tracker.start_tracking()
    tracker.start_capturing(gap=1)  # Capture every 5 minutes

    try:
        while True:
            print(f"Worked hours: {tracker.calc_work_hours()}")
            time.sleep(10)  # Update display every 10 seconds

    except KeyboardInterrupt:
        tracker.stop_capturing()
        print(f"\nFinal work duration: {tracker.calc_work_hours()}")
