import sys
import threading
import time
from datetime import datetime
from tkinter import messagebox

import customtkinter as ctk

from src.argus.exceptions import CustomException
from src.argus.logger import logging
from src.argus.mousetracking.clicktracker import ClickTracker
from src.argus.screenshot.capture import ScreenshotCapture
from src.argus.utils.utils import get_random_interval, show_temp_dialog, has_internet_connection, ask_yes_no_dialog


class ModernProgressBar(ctk.CTkFrame):
    """Custom animated progress bar for work sessions"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.progress = ctk.CTkProgressBar(self, width=300, height=8)
        self.progress.pack(pady=5)
        self.progress.set(0)

    def update_progress(self, value: float):
        """Update progress bar value (0-1)"""
        self.progress.set(value)


class StatusIndicator(ctk.CTkFrame):
    """Modern status indicator with animated dots"""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.status_text = ctk.CTkLabel(self, text="● Ready", font=("Arial", 14, "bold"))
        self.status_text.pack()
        self.animation_dots = 0

    def set_status(self, status: str, color: str):
        """Set status with color coding"""
        colors = {
            "ready": "#3498db",
            "running": "#2ecc71",
            "paused": "#f39c12",
            "stopped": "#e74c3c",
            "error": "#e74c3c"
        }

        status_icons = {
            "ready": "●",
            "running": "▶",
            "paused": "⏸",
            "stopped": "⏹",
            "error": "⚠"
        }

        icon = status_icons.get(status.lower(), "●")
        self.status_text.configure(
            text=f"{icon} {status.title()}",
            text_color=colors.get(status.lower(), color)
        )

    def animate_working(self):
        """Animate status when working"""
        if hasattr(self, '_animating') and self._animating:
            dots = "." * (self.animation_dots % 4)
            self.status_text.configure(text=f"▶ Working{dots}")
            self.animation_dots += 1
            self.after(500, self.animate_working)

    def start_animation(self):
        """Start working animation"""
        self._animating = True
        self.animate_working()

    def stop_animation(self):
        """Stop working animation"""
        self._animating = False


class MainAppUI:

    def __init__(self, user_id_num: str, username: str):
        # Core components
        self.user_id_num = user_id_num
        self.user_name = username

        # Initialize tracking components with error handling
        try:
            self.click_tracker = ClickTracker(inactivity_threshold=120)
            self.click_tracker.callback = self._handle_inactivity
            self.capture = ScreenshotCapture(self.click_tracker)
        except Exception as e:
            logging.error(f"Failed to initialize tracking components: {e}")
            messagebox.showerror("Initialization Error", f"Failed to initialize tracking: {e}")
            sys.exit(1)

        # UI state management
        self.is_internet_connected = False
        self.last_internet_check = None
        self.work_session_start = None

        # Initialize UI
        self._setup_main_window()
        self._create_widgets()
        self._start_background_tasks()

    def _setup_main_window(self):
        """Setup main window with modern styling"""
        self.root = ctk.CTk()
        self.root.title("Argus Work Tracker v1.0")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        # Modern dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (400 // 2)
        self.root.geometry(f"600x500+{x}+{y}")

        # Setup window close handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)

    def _create_widgets(self):
        """Create and layout all UI widgets with modern design"""

        # Main container with padding
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Header section
        self._create_header_section(main_container)

        # Status section
        self._create_status_section(main_container)

        # Control buttons section
        self._create_control_section(main_container)

        # Progress and time section
        self._create_progress_section(main_container)

        # Footer section
        self._create_footer_section(main_container)

        # Show initial connection warning
        show_temp_dialog(
            self.root,
            "Notice",
            "⚠ Ensure stable internet connection\nOtherwise your progress will be lost.",
            duration=4000
        )

    def _create_header_section(self, parent):
        """Create header with user info and internet status"""
        header_frame = ctk.CTkFrame(parent, height=80, fg_color="#2c3e50")
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Argus Tracker",
            font=("Arial", 24, "bold"),
            text_color="#ecf0f1"
        )
        title_label.pack(pady=(10, 0))

        # User info
        user_info = ctk.CTkLabel(
            header_frame,
            text=f"👤 {self.user_name} (ID: {self.user_id_num})",
            font=("Arial", 12),
            text_color="#bdc3c7"
        )
        user_info.pack(pady=(0, 10))

        # Internet status (top right)
        self.internet_label = ctk.CTkLabel(
            header_frame,
            text="🔍 Checking...",
            font=("Arial", 10),
            text_color="#95a5a6"
        )
        self.internet_label.place(relx=1.0, rely=0.0, anchor="ne", x=-15, y=15)

    def _create_status_section(self, parent):
        """Create status indicator section"""
        status_frame = ctk.CTkFrame(parent, fg_color="transparent")
        status_frame.pack(fill="x", pady=(0, 20))

        self.status_indicator = StatusIndicator(status_frame)
        self.status_indicator.pack()

    def _create_control_section(self, parent):
        """Create control buttons with modern styling"""
        control_frame = ctk.CTkFrame(parent, fg_color="transparent")
        control_frame.pack(pady=(0, 20))

        # Button styling
        button_config = {
            "width": 100,
            "height": 40,
            "font": ("Arial", 12, "bold"),
            "corner_radius": 8
        }

        self.start_btn = ctk.CTkButton(
            control_frame,
            text="▶ Start",
            command=self._safe_start_capture,
            fg_color="#27ae60",
            hover_color="#2ecc71",
            **button_config
        )
        self.start_btn.pack(side="left", padx=10)

        self.pause_btn = ctk.CTkButton(
            control_frame,
            text="⏸ Pause",
            command=self._safe_toggle_pause,
            fg_color="#f39c12",
            hover_color="#e67e22",
            state="disabled",
            **button_config
        )
        self.pause_btn.pack(side="left", padx=10)

        self.stop_btn = ctk.CTkButton(
            control_frame,
            text="⏹ Stop",
            command=self._safe_stop_capture,
            fg_color="#c0392b",
            hover_color="#e74c3c",
            state="disabled",
            **button_config
        )
        self.stop_btn.pack(side="left", padx=10)

    def _create_progress_section(self, parent):
        """Create progress tracking section"""
        progress_frame = ctk.CTkFrame(parent, height=120)
        progress_frame.pack(fill="x", pady=(0, 20))
        progress_frame.pack_propagate(False)

        # Time display
        self.time_label = ctk.CTkLabel(
            progress_frame,
            text="⏱ Work time: 00:00:00",
            font=("Arial", 16, "bold"),
            text_color="#3498db"
        )
        self.time_label.pack(pady=(15, 10))

        # Progress bar
        self.progress_bar = ModernProgressBar(progress_frame)
        self.progress_bar.pack(pady=(0, 15))

        # Session info
        self.session_label = ctk.CTkLabel(
            progress_frame,
            text="📊 Session: Not started",
            font=("Arial", 14),
            text_color="#7f8c8d"
        )
        self.session_label.pack()

    def _create_footer_section(self, parent):
        """Create footer with additional info"""
        footer_frame = ctk.CTkFrame(parent, height=60, fg_color="#34495e")
        footer_frame.pack(fill="x")
        footer_frame.pack_propagate(False)

        self.info_label = ctk.CTkLabel(
            footer_frame,
            text="💡 Tip: Keep this window open / minimized during work session",
            font=("Arial", 13),
            text_color="#95a5a6"
        )
        self.info_label.pack(expand=True)

    def _safe_start_capture(self):
        """Safely start capture with error handling"""
        try:
            if has_internet_connection():
                self.start_capture()
            else:
                self.is_internet_connected = False
                show_temp_dialog(self.root, "Notice", message="Please check your internet connection and try again", duration=3500)
        except Exception as e:
            self._handle_error("Start Capture", e)

    def _safe_toggle_pause(self):
        """Safely toggle pause with error handling"""
        try:
            self.toggle_pause()
        except Exception as e:
            self._handle_error("Toggle Pause", e)

    def _safe_stop_capture(self):
        """Safely stop capture with error handling"""
        try:
            self.stop_capture()
        except Exception as e:
            self._handle_error("Stop Capture", e)

    def start_capture(self):
        """Start capture with enhanced validation and UI updates"""

        if not self.user_id_num:
            self._show_error("User ID not found. Please log in again!")
            self.root.after(2000, self.root.quit)
            return

        if not self.is_internet_connected:
            response = ask_yes_no_dialog(
                "No Internet Connection",
                "No internet connection detected. Screenshots may not be uploaded. Continue anyway?"
            )
            if not response:
                return

        # Start capture
        self.capture.start(self.user_id_num)
        self.work_session_start = datetime.now()

        # Update UI
        self._update_button_states(start=False, pause=True, stop=True)
        self.status_indicator.set_status("running", "#2ecc71")
        self.status_indicator.start_animation()
        self.session_label.configure(text=f"📊 Session started: {self.work_session_start.strftime('%H:%M:%S')}")
        self.info_label.configure(text="🏁 Session running")

        # Capture initial screenshot
        self.capture.capture()

        # Start background tasks
        threading.Thread(target=self._run_capture_loop, daemon=True).start()
        self._update_work_time()

        logging.info("Capture started successfully")

    def toggle_pause(self):
        """Enhanced pause/resume with better UI feedback"""
        if self.capture.is_paused:
            # Resume
            self.click_tracker.ignore_ui_clicks(2)
            self.click_tracker.reset_inactivity_timer()

            self.capture.resume()
            self.pause_btn.configure(text="⏸ Pause")
            self.status_indicator.set_status("running", "#2ecc71")
            self.status_indicator.start_animation()
            self.info_label.configure(text="✅ Resumed tracking")

        else:
            # Pause
            self.click_tracker.ignore_ui_clicks(2)

            self.capture.pause()
            self.pause_btn.configure(text="▶ Resume")
            self.status_indicator.set_status("paused", "#f39c12")
            self.status_indicator.stop_animation()
            self.info_label.configure(text="⏸ Tracking paused")

    def stop_capture(self):
        """Enhanced stop with session summary"""
        if hasattr(self, 'work_session_start') and self.work_session_start:
            session_duration = datetime.now() - self.work_session_start
            hours, remainder = divmod(int(session_duration.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)

            # show_temp_dialog(self.root, title="Session Completed",
            #                  message=f"Work session completed!\nDuration: {hours:02d}:{minutes:02d}:{seconds:02d}")

            messagebox.showinfo(
                "Session Complete",
                f"Work session completed!\nDuration: {hours:02d}:{minutes:02d}:{seconds:02d}"
            )

        self.session_label.configure(text="Stopping, please wait!")
        self.info_label.configure(text="Uploading screenshot")
        # Upload last image
        self.capture.capture()

        self._update_button_states(start=True, pause=False, stop=False)
        self.status_indicator.set_status("stopped", "#e74c3c")
        self.capture.stop()
        self.status_indicator.stop_animation()
        self.session_label.configure(text="Last Session Completed")
        self.info_label.configure(text="Screenshot Uploaded")


        logging.info("Capture stopped")

    def _handle_inactivity(self, activity: bool):
        """Enhanced inactivity handling with better logging"""
        logging.debug(f"Inactivity handler called: activity={activity}")

        try:
            if activity:
                if self.capture.is_running and self.capture.is_paused:
                    logging.info("Auto-resuming due to mouse activity")
                    self.capture.resume()
                    self.pause_btn.configure(text="⏸ Pause")
                    self.status_indicator.set_status("running", "#2ecc71")
                    self.status_indicator.start_animation()
                    self.info_label.configure(text="🖱 Auto-resumed (mouse activity detected)")
            else:
                if self.capture.is_running and not self.capture.is_paused:
                    logging.info("Auto-pausing due to inactivity")
                    self.capture.pause()
                    self.pause_btn.configure(text="▶ Resume")
                    self.status_indicator.set_status("paused", "#f39c12")
                    self.status_indicator.stop_animation()
                    self.info_label.configure(text="😴 Auto-paused (inactive)")

        except Exception as e:
            logging.error(f"Error in inactivity handler: {e}")

    def _run_capture_loop(self):
        """Enhanced capture loop with better error handling"""
        while self.capture.is_running:
            try:
                if not self.capture.is_paused:
                    random_time = get_random_interval()
                    logging.debug(f"Next capture in {random_time} seconds")
                    time.sleep(random_time)

                    if self.capture.is_running:
                        success = self.capture.capture()
                        status_text = "✅ Upload successful" if success else "❌ Upload failed"
                        color = "#2ecc71" if success else "#e74c3c"

                        self.root.after(0, lambda: self.info_label.configure(
                            text=status_text, text_color=color
                        ))
                else:
                    time.sleep(1)  # Check every second when paused

            except Exception as e:
                logging.error(f"Error in capture loop: {e}")
                self.root.after(0, lambda: self._handle_error("Capture Loop", e))
                time.sleep(5)  # Wait before retrying

    def _update_work_time(self):
        """Enhanced work time display with progress tracking"""
        if self.capture.is_running:
            try:
                working_hours = self.capture.get_work_hours()
                self.time_label.configure(text=f"⏱ Work time: {working_hours}")

                # Update progress bar (assuming 8-hour workday)
                if hasattr(self.capture, 'get_elapsed_time'):
                    elapsed_seconds = self.capture.get_elapsed_time().total_seconds()
                    progress = min(elapsed_seconds / (9 * 3600), 1.0)  # 8 hours max
                    self.progress_bar.update_progress(progress)

                self.root.after(1000, self._update_work_time)

            except Exception as e:
                logging.error(f"Error updating work time: {e}")
                self.root.after(5000, self._update_work_time)  # Retry in 5 seconds

    def _check_internet_periodically(self):
        """Enhanced internet checking with better UI feedback"""
        try:
            self.is_internet_connected = has_internet_connection()

            if self.is_internet_connected and self.capture.is_running:
                try:
                    self.capture._upload_pending_screenshots()
                except Exception as e:
                    logging.warning(f"Error uploading pending screenshots: {e}")
            self.last_internet_check = datetime.now()

            if self.is_internet_connected:
                self.internet_label.configure(
                    text="🌐 Connected",
                    text_color="#2ecc71"
                )
            else:
                self.internet_label.configure(
                    text="📡 Offline",
                    text_color="#e74c3c"
                )

        except Exception as e:
            logging.warning(f"Error checking internet: {e}")
            self.internet_label.configure(
                text="❓ Unknown",
                text_color="#f39c12"
            )

        # Schedule next check
        self.root.after(4000, self._check_internet_periodically)

    def _start_background_tasks(self):
        """Start all background tasks"""
        self._check_internet_periodically()

    def _update_button_states(self, start: bool, pause: bool, stop: bool):
        """Update button states consistently"""
        states = {
            self.start_btn: "normal" if start else "disabled",
            self.pause_btn: "normal" if pause else "disabled",
            self.stop_btn: "normal" if stop else "disabled"
        }

        for button, state in states.items():
            button.configure(state=state)

    def _handle_error(self, operation: str, error: Exception):
        """Centralized error handling"""
        error_msg = f"Error in {operation}: {str(error)}"
        logging.error(error_msg)

        self.status_indicator.set_status("error", "#e74c3c")
        self.info_label.configure(text=f"❌ {error_msg}", text_color="#e74c3c")

        # Show error dialog for critical errors
        if "critical" in str(error).lower():
            messagebox.showerror("Critical Error", error_msg)

    def _show_error(self, message: str):
        """Show error message in UI"""
        self.status_indicator.set_status("error", "#e74c3c")
        self.info_label.configure(text=f"❌ {message}", text_color="#e74c3c")

    def _on_window_close(self):
        """Handle window close event gracefully"""
        if hasattr(self, 'capture') and self.capture.is_running:
            response = messagebox.askyesno(
                "Confirm Exit",
                "Tracking is still active. Stop tracking and exit?"
            )
            if response:
                self.stop_capture()
                self.root.destroy()
        else:
            self.root.destroy()

    def run(self):
        """Run the application with comprehensive error handling"""
        try:
            logging.info("Starting Argus UI application")
            self.root.mainloop()
            logging.info("Application closed normally")

        except KeyboardInterrupt:
            logging.info("Application interrupted by user")

        except Exception as e:
            logging.critical(f"Critical error in main application: {e}")
            messagebox.showerror(
                "Critical Error",
                f"Application encountered a critical error:\n{e}\n\nPlease restart the application."
            )
            raise CustomException(e, sys)

        finally:
            # Cleanup
            if hasattr(self, 'capture') and self.capture.is_running:
                self.capture.stop()
            logging.info("Application cleanup completed")
