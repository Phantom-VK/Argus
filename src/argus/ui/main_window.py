import sys
import time

import customtkinter as ctk
import threading

from src.argus.exceptions import CustomException
from src.argus.mousetracking.clicktracker import ClickTracker
from src.argus.screenshot.capture import ScreenshotCapture
from src.argus.logger import logging

class AppUI:
    def __init__(self):
        self.click_tracker = ClickTracker(inactivity_threshold=60)
        self.click_tracker.callback = self._handle_inactivity
        self.capture = ScreenshotCapture(self.click_tracker)
        self.root = ctk.CTk()
        self.root.title("Argus Screenshot Tracker")
        self.root.geometry("400x250")
        ctk.set_appearance_mode("dark")
        self.create_widgets()

    def create_widgets(self):
        # User ID Entry
        self.user_entry = ctk.CTkEntry(self.root, placeholder_text="Enter your user ID", width=250)
        self.user_entry.pack(pady=10)

        # Button Frame
        self.button_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.button_frame.pack(pady=5)

        self.start_btn = ctk.CTkButton(self.button_frame, text="Start", command=self.start_capture,
                                       fg_color="#2ecc71", width=80)
        self.start_btn.pack(side="left", padx=5)

        self.pause_btn = ctk.CTkButton(self.button_frame, text="Pause", command=self.toggle_pause,
                                       fg_color="#f39c12", width=80, state="disabled")
        self.pause_btn.pack(side="left", padx=5)

        self.stop_btn = ctk.CTkButton(self.button_frame, text="Stop", command=self.stop_capture,
                                      fg_color="#e74c3c", width=80, state="disabled")
        self.stop_btn.pack(side="left", padx=5)

        # Status Display
        self.status_label = ctk.CTkLabel(self.root, text="Status: Ready", text_color="#3498db")
        self.status_label.pack(pady=5)

        self.time_label = ctk.CTkLabel(self.root, text="Work time: 00:00:00")
        self.time_label.pack()

    def start_capture(self):
        user_id = self.user_entry.get().strip()
        if not user_id:
            self.status_label.configure(text="Please enter user ID!", text_color="#e74c3c")
            return

        self.capture.start(user_id)
        self.start_btn.configure(state="disabled")
        self.pause_btn.configure(state="normal")
        self.stop_btn.configure(state="normal")
        self.user_entry.configure(state="disabled")
        self.status_label.configure(text="Status: Running", text_color="#2ecc71")

        #Capture Initial shot
        self.capture.capture()

        threading.Thread(target=self.run_capture_loop, daemon=True).start()
        self.update_work_time()

    def toggle_pause(self):
        if self.capture.is_paused:
            self.capture.resume()
            self.pause_btn.configure(text="Pause")
            self.status_label.configure(text="Status: Running", text_color="#2ecc71")
        else:
            self.capture.pause()
            self.pause_btn.configure(text="Resume")
            self.status_label.configure(text="Status: Paused", text_color="#f39c12")

    def stop_capture(self):
        self.capture.stop()
        self.start_btn.configure(state="normal")
        self.pause_btn.configure(state="disabled")
        self.stop_btn.configure(state="disabled")
        self.user_entry.configure(state="normal")
        self.status_label.configure(text="Status: Stopped", text_color="#e74c3c")

    def _handle_inactivity(self, activity:bool):
        if activity:
            if self.capture.is_running and self.capture.is_paused:
                self.toggle_pause()
        else:
            self.toggle_pause()

    def run_capture_loop(self):
        while self.capture.is_running:
            if not self.capture.is_paused:
                random_time = self.capture.get_random_interval()
                # print(f"Random time: {random_time}")
                time.sleep(random_time)
                if self.capture.is_running:
                    success = self.capture.capture()
                    self.root.after(0, lambda: self.status_label.configure(
                        text=f"Last upload: {'Success' if success else 'Failed'}",
                        text_color="#2ecc71" if success else "#e74c3c"
                    ))

    def update_work_time(self):
        if self.capture.is_running:
            working_hours = self.capture.get_work_hours()
            self.time_label.configure(text=f"Work time: {working_hours}")
            self.root.after(1000, self.update_work_time)



    def run(self):
        try:
            self.root.mainloop()
            logging.info("Inside mainloop")
        except Exception as e:
            raise CustomException(e, sys)