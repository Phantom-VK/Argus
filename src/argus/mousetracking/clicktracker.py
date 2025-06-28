from datetime import datetime
from pynput import mouse
import threading
from src.argus.logger import logging


class ClickTracker:
    def __init__(self, inactivity_threshold=1800):  # 30 minutes
        self.is_paused = False
        self.last_click_time = datetime.now()
        self.inactivity_threshold = inactivity_threshold
        self.callback = None
        self.listener = None
        self.monitor_activity = False
        self.ignore_next_clicks = 0

    def on_click(self, x, y, button, pressed):
        if pressed:
            # Ignore clicks that are from UI interaction
            if self.ignore_next_clicks > 0:
                self.ignore_next_clicks -= 1
                print(f"Ignoring UI click at {datetime.now()}")
                return

            self.last_click_time = datetime.now()
            print(f"Real mouse activity detected at {self.last_click_time}")
            self.callback(activity=True)  # Notify of activity

    def start_monitoring(self):
        self.listener = mouse.Listener(on_click=self.on_click)
        self.listener.start()
        self.last_click_time = datetime.now()
        logging.info("ClickTracker started")
        self.monitor_activity = True
        threading.Thread(target=self._monitor_inactivity, daemon=True).start()

    def _monitor_inactivity(self):
        while self.monitor_activity:
            time_since_last_click = (datetime.now() - self.last_click_time).total_seconds()
            print(f"Time since last click {time_since_last_click}")

            # Only trigger inactivity if we're currently active
            if (time_since_last_click > self.inactivity_threshold
                    and self.callback
                    and not self.is_paused):
                print("Triggering inactivity callback")
                self.callback(activity=False)

            threading.Event().wait(10)

    def ignore_ui_clicks(self, count=2):
        """Ignore next N clicks as they are from UI interaction"""
        self.ignore_next_clicks = count
        print(f"Will ignore next {count} UI clicks")

    def reset_inactivity_timer(self):
        """Reset the last click time to prevent immediate inactivity detection"""
        self.last_click_time = datetime.now()
        print(f"Inactivity timer reset at {self.last_click_time}")

    def stop_monitoring(self):
        if self.listener:
            self.listener.stop()
            self.monitor_activity = False