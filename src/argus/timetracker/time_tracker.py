from src.argus.logger import logging
from datetime import datetime, timedelta
from typing import List, Tuple


class TimeTracker:
    def __init__(self):
        self.start_time = None
        self.is_paused = False
        self.current_pause_start = None
        self.pause_sessions: List[Tuple[datetime, datetime]] = []
        self.total_paused_time = timedelta()

    def start(self):
        """Start tracking for the first time"""
        if self.start_time is None:
            self.start_time = datetime.now()
            self.is_paused = False
            logging.info(f"Time tracker started at {self.start_time}")
        else:
            logging.warning("Time tracker already started. Use resume() to continue after pause.")

    def pause(self):
        """Pause tracking"""
        if not self.is_paused and self.start_time:
            self.current_pause_start = datetime.now()
            self.is_paused = True
            logging.info(f"Time tracker paused at {self.current_pause_start}")
        else:
            logging.warning("Time tracker is already paused or not started")

    def resume(self):
        """Resume tracking after pause"""
        if self.is_paused and self.current_pause_start:
            pause_end = datetime.now()
            # Record this pause session
            pause_duration = pause_end - self.current_pause_start
            self.pause_sessions.append((self.current_pause_start, pause_end))
            self.total_paused_time += pause_duration

            # Reset pause state
            self.is_paused = False
            self.current_pause_start = None

            logging.info(f"Time tracker resumed at {pause_end}. Pause duration: {pause_duration}")
        else:
            logging.warning("Time tracker is not paused or not started")

    def reset_all_time(self):
        """Reset all tracking data"""
        self.start_time = None
        self.is_paused = False
        self.current_pause_start = None
        self.pause_sessions.clear()
        self.total_paused_time = timedelta()
        logging.info("Time tracker reset")

    def get_elapsed_time(self) -> timedelta:
        """Get actual worked time (excluding all paused time)"""
        if not self.start_time:
            return timedelta()

        current_time = datetime.now()
        total_time = current_time - self.start_time

        # Subtract all completed pause sessions
        total_paused = self.total_paused_time

        # If currently paused, add current pause duration
        if self.is_paused and self.current_pause_start:
            current_pause_duration = current_time - self.current_pause_start
            total_paused += current_pause_duration

        # Return worked time (total - paused)
        worked_time = total_time - total_paused
        return max(worked_time, timedelta())  # Ensure non-negative

    def get_formatted_time(self) -> str:
        """Format time as HH:MM:SS"""
        elapsed = self.get_elapsed_time()
        total_seconds = int(elapsed.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def get_time_in_sec(self) -> float:
        """Get elapsed time in seconds"""
        return self.get_elapsed_time().total_seconds()

    def get_paused_duration_between(self, start_time: datetime, end_time: datetime) -> timedelta:
        """Calculate total paused duration between two timestamps"""
        if not self.start_time or start_time >= end_time:
            return timedelta()

        total_paused = timedelta()

        # Check completed pause sessions
        for pause_start, pause_end in self.pause_sessions:
            # Find overlap between pause session and time range
            overlap_start = max(pause_start, start_time)
            overlap_end = min(pause_end, end_time)

            if overlap_start < overlap_end:
                total_paused += overlap_end - overlap_start

        # Check current pause session if active
        if self.is_paused and self.current_pause_start:
            current_pause_start = self.current_pause_start
            current_time = datetime.now()

            # Find overlap with current pause
            overlap_start = max(current_pause_start, start_time)
            overlap_end = min(current_time, end_time)

            if overlap_start < overlap_end:
                total_paused += overlap_end - overlap_start

        return total_paused

    def get_active_time_between(self, start_time: datetime, end_time: datetime) -> timedelta:
        """Get active (non-paused) time between two timestamps"""
        if start_time >= end_time:
            return timedelta()

        total_time = end_time - start_time
        paused_time = self.get_paused_duration_between(start_time, end_time)
        active_time = total_time - paused_time

        return max(active_time, timedelta())  # Ensure non-negative

    def get_debug_info(self) -> dict:
        """Get debug information about current state"""
        return {
            "start_time": self.start_time,
            "is_paused": self.is_paused,
            "current_pause_start": self.current_pause_start,
            "pause_sessions_count": len(self.pause_sessions),
            "total_paused_time": self.total_paused_time,
            "elapsed_time": self.get_elapsed_time(),
            "formatted_time": self.get_formatted_time()
        }