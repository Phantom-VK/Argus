from datetime import datetime
from pynput import mouse
import threading

class ClickTracker:
    def __init__(self, inactivity_threshold=1800):  # 30 minutes
        self.last_click_time = datetime.now()
        self.inactivity_threshold = inactivity_threshold
        self.callback = None
        self.listener = None

    def on_click(self, x, y, button, pressed):
        if pressed:
            self.last_click_time = datetime.now()
            if self.callback:
                self.callback(active=True)  # Notify of activity

    def start_monitoring(self, callback=None):
        self.callback = callback
        self.listener = mouse.Listener(on_click=self.on_click)
        self.listener.start()
        threading.Thread(target=self._monitor_inactivity, daemon=True).start()

    def _monitor_inactivity(self):
        while True:
            time_since_last_click = (datetime.now() - self.last_click_time).total_seconds()
            if time_since_last_click > self.inactivity_threshold and self.callback:
                self.callback(active=False)  # Notify of inactivity
            threading.Event().wait(10)  # Check every 10 seconds

    def stop_monitoring(self):
        if self.listener:
            self.listener.stop()