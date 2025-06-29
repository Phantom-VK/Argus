import os
import sys
from collections import deque
from datetime import datetime, timedelta

import mss
import mss.tools

from src.argus.api.tracker import api_client
from src.argus.exceptions import CustomException
from src.argus.filemanager.file_manager import file_manager
from src.argus.logger import logging
from src.argus.mousetracking.clicktracker import ClickTracker
from src.argus.timetracker.time_tracker import TimeTracker
from src.argus.utils.utils import has_internet_connection


class ScreenshotCapture:
    def __init__(self, clicktracker: ClickTracker):
        self.is_running = False
        self.is_paused = False
        self.user_id = ""
        self.screenshot_dir = ""
        self.click_tracker = clicktracker
        self.file_manager = file_manager
        self.last_capture_time = None
        self.session_start_time = None
        self.pending_uploads = deque()
        self.time_tracker = TimeTracker()

    def start(self, user_id: str):
        """Start the tracking session"""
        self.user_id = user_id
        self.screenshot_dir = self.file_manager.get_screenshot_path(self.user_id)

        self.is_running = True
        self.is_paused = False
        self.session_start_time = datetime.now()
        self.last_capture_time = None  # Reset for new session

        # Start time tracker
        self.time_tracker.start()

        # Start click tracker
        self.click_tracker.is_paused = False
        self.click_tracker.start_monitoring()

        logging.info(f"Tracking started for user {user_id} at {self.session_start_time}")

    def pause(self):
        """Pause the tracking"""
        if self.is_running and not self.is_paused:
            self.is_paused = True
            self.time_tracker.pause()
            self.click_tracker.is_paused = True
            logging.info("Tracking paused")
        else:
            logging.warning("Cannot pause - not running or already paused")

    def resume(self):
        """Resume tracking after pause"""
        if self.is_running and self.is_paused:
            self.is_paused = False
            self.time_tracker.resume()
            self.click_tracker.is_paused = False
            logging.info("Tracking resumed")
        else:
            logging.warning("Cannot resume - not running or not paused")

    def stop(self):
        """Stop the tracking session"""
        if self.is_running:
            self.is_running = False
            self.is_paused = False

            # Stop click tracker
            self.click_tracker.stop_monitoring()

            # Log final statistics
            total_work_time = self.time_tracker.get_formatted_time()
            logging.info(f"Tracking stopped. Total work hours: {total_work_time}")

            # Debug info
            debug_info = self.time_tracker.get_debug_info()
            logging.info(f"Session debug info: {debug_info}")

            # Reset trackers
            self.time_tracker.reset_all_time()
            self.last_capture_time = None
            self.session_start_time = None
        else:
            logging.warning("Tracking is not running")

    def capture(self) -> bool:
        """Capture screenshot and calculate accurate time gap"""
        if not self.is_running:
            logging.warning("Cannot capture - tracking not running")
            return False

        if self.is_paused:
            logging.warning("Cannot capture - tracking is paused")
            return False

        current_time = datetime.now()

        # Calculate time gap between screenshots (excluding paused time)
        if self.last_capture_time is None:
            # First capture - calculate from session start
            time_gap_seconds = self.time_tracker.get_active_time_between(
                self.session_start_time, current_time
            ).total_seconds()
            logging.info(f"First capture - time since session start: {time_gap_seconds:.2f} seconds")
        else:
            # Subsequent captures - calculate from last capture
            time_gap_seconds = self.time_tracker.get_active_time_between(
                self.last_capture_time, current_time
            ).total_seconds()
            logging.info(f"Time gap from last capture: {time_gap_seconds:.2f} seconds")

        # Update last capture time
        self.last_capture_time = current_time

        # Generate filename and filepath
        filename = f"screenshot_{current_time.strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.screenshot_dir, filename)

        try:
            # Capture screenshot
            success = self._take_screenshot(filepath)
            if not success:
                return False

            # Upload activity data
            logging.info(f"Uploading activity - Work seconds: {time_gap_seconds:.2f}")
            if has_internet_connection():
                upload_success = api_client.upload_activity(
                    employee_id=self.user_id,
                    screenshot_path=filepath,
                    work_seconds=str(time_gap_seconds)
                )
                if upload_success:
                    logging.info("Screenshot and activity uploaded successfully")
                    # Try uploading any pending screenshots
                    self._upload_pending_screenshots()
                    return True
                else:
                    logging.warning("Failed to upload current screenshot, queued for later")
                    self.pending_uploads.append((filepath, time_gap_seconds))
                    return False
            else:
                logging.warning("No internet: storing screenshot in pending queue")
                self.pending_uploads.append((filepath, time_gap_seconds))
                return False


        except Exception as e:
            logging.error(f"Error during capture: {str(e)}")
            raise CustomException(e, sys)

    def _upload_pending_screenshots(self):
        """Try uploading any stored screenshots"""
        logging.info("Checking for pending uploads...")
        while self.pending_uploads and has_internet_connection():
            filepath, work_seconds = self.pending_uploads.popleft()
            try:
                success = api_client.upload_activity(
                    employee_id=self.user_id,
                    screenshot_path=filepath,
                    work_seconds=str(work_seconds)
                )
                if success:
                    logging.info(f"Pending screenshot uploaded: {filepath}")
                else:
                    logging.warning(f"Retrying later: {filepath}")
                    self.pending_uploads.appendleft((filepath, work_seconds))
                    break  # Stop trying if one fails
            except Exception as e:
                logging.error(f"Error uploading pending screenshot: {e}")
                self.pending_uploads.appendleft((filepath, work_seconds))
                break

    def _take_screenshot(self, filepath: str) -> bool:
        """Take screenshot of all monitors"""
        try:
            with mss.mss() as sct:
                # Get all monitor areas (excluding monitor 0 which is virtual combined)
                if len(sct.monitors) <= 1:
                    logging.error("No monitors detected")
                    return False

                monitor_areas = [sct.monitors[i] for i in range(1, len(sct.monitors))]

                # Calculate combined screen area
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

                # Save screenshot
                mss.tools.to_png(screenshot.rgb, screenshot.size, output=filepath)
                logging.info(f"Screenshot captured and saved: {filepath}")
                return True

        except Exception as e:
            logging.error(f"Screenshot capture failed: {str(e)}")
            return False

    def get_work_hours(self) -> str:
        """Get formatted work hours for current session"""
        return self.time_tracker.get_formatted_time()

    def get_work_seconds(self) -> float:
        """Get work time in seconds for current session"""
        return self.time_tracker.get_time_in_sec()

    def get_session_info(self) -> dict:
        """Get detailed session information"""
        return {
            "is_running": self.is_running,
            "is_paused": self.is_paused,
            "user_id": self.user_id,
            "session_start_time": self.session_start_time,
            "last_capture_time": self.last_capture_time,
            "work_hours": self.get_work_hours(),
            "work_seconds": self.get_work_seconds(),
            "time_tracker_debug": self.time_tracker.get_debug_info()
        }