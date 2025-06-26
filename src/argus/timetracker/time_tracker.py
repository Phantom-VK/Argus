import random

from src.argus.logger import logging
from datetime import datetime, timedelta


class TimeTracker:
    def __init__(self):
        self.start_time = None
        self.total_paused_time = timedelta()
        self.last_pause_time = None
        self.is_paused = False

    def start(self):
        """Start or resume tracking"""
        logging.info("Time tracker started")
        if self.start_time is None:
            self.start_time = datetime.now()
        elif self.is_paused:
            self.total_paused_time += datetime.now() - self.last_pause_time
            self.is_paused = False

    def pause(self):
        """Pause tracking"""
        if not self.is_paused:
            self.last_pause_time = datetime.now()
            self.is_paused = True

    def get_elapsed_time(self) -> timedelta:
        """Get actual worked time (excluding paused time)"""
        if not self.start_time:
            return timedelta()

        if self.is_paused:
            return (self.last_pause_time - self.start_time) - self.total_paused_time
        return (datetime.now() - self.start_time) - self.total_paused_time

    def get_formatted_time(self) -> str:
        """Format time as HH:MM:SS"""
        elapsed = self.get_elapsed_time()
        hours, remainder = divmod(elapsed.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def get_time_in_sec(self) -> str:
        return str(self.get_elapsed_time().total_seconds())

    def get_paused_duration_since(self, since_time: datetime) -> timedelta:
        """Calculate total paused duration since given timestamp"""
        if not self.last_pause_time or since_time > self.last_pause_time:
            return timedelta()
        return datetime.now() - self.last_pause_time


def get_random_interval() -> int:
    return random.randint(120, 180)