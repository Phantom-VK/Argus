import sys

import customtkinter as ctk

from src.argus.api.auth import AuthAPI
from src.argus.exceptions import CustomException
from src.argus.ui.main_window import MainAppUI
from src.argus.ui.register_window import RegisterWindow


class LoginAppUI:
    def __init__(self):
        # Initialize the main window
        self.root = ctk.CTk()
        self.root.title("Argus Work Tracker")
        self.root.geometry("450x650")
        self.root.resizable(False, False)

        # Set appearance mode and color theme
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # Center the window on screen
        self._center_window()

        # Create UI components
        self._create_widgets()

        # Bind Enter key to login
        self.root.bind('<Return>', lambda event: self.login())

        # Initialize variables for input validation
        self.is_logging_in = False

    def _center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 450) // 2
        y = (screen_height - 650) // 2
        self.root.geometry(f"450x650+{x}+{y}")

    def _create_widgets(self):
        """Create and arrange all UI widgets"""
        # Main container frame
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # Header section
        self._create_header()

        # Login form section
        self._create_login_form()

        # Action buttons section
        self._create_action_buttons()

        # Status section
        self._create_status_section()

        # Footer section
        self._create_footer()

        # Ensure app closes properly when window is closed
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

    def _create_header(self):
        """Create the header section with title and logo placeholder"""
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        # App title
        title_label = ctk.CTkLabel(
            header_frame,
            text="🔐 ARGUS",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.pack(pady=(0, 5))

        # Subtitle
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Work Tracking System",
            font=ctk.CTkFont(size=16),
            text_color="gray"
        )
        subtitle_label.pack()

    def _create_login_form(self):
        """Create the login form with input fields"""
        form_frame = ctk.CTkFrame(self.main_frame, corner_radius=15)
        form_frame.pack(fill="x", pady=(0, 15))

        # Form title
        form_title = ctk.CTkLabel(
            form_frame,
            text="Sign In to Your Account",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        form_title.pack(pady=(15, 20))

        # Login ID field
        self.login_id_label = ctk.CTkLabel(form_frame, text="Login ID", anchor="w")
        self.login_id_label.pack(fill="x", padx=30, pady=(0, 5))

        self.login_id = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter your login ID",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.login_id.pack(fill="x", padx=30, pady=(0, 15))

        # Password field
        self.password_label = ctk.CTkLabel(form_frame, text="Password", anchor="w")
        self.password_label.pack(fill="x", padx=30, pady=(0, 5))

        self.password = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter your password",
            show="*",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.password.pack(fill="x", padx=30, pady=(0, 20))

        # Show/Hide password toggle
        self.show_password_var = ctk.BooleanVar()
        self.show_password_checkbox = ctk.CTkCheckBox(
            form_frame,
            text="Show password",
            variable=self.show_password_var,
            command=self._toggle_password_visibility
        )
        self.show_password_checkbox.pack(anchor="w", padx=30, pady=(0, 15))

    def _create_action_buttons(self):
        """Create login and register buttons"""
        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 15))

        # Login button
        self.login_btn = ctk.CTkButton(
            button_frame,
            text="Sign In",
            command=self.login,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=10
        )
        self.login_btn.pack(fill="x", padx=30, pady=(0, 10))

        # Divider
        divider_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
        divider_frame.pack(fill="x", padx=30, pady=10)

        divider_line1 = ctk.CTkFrame(divider_frame, height=1, fg_color="gray")
        divider_line1.pack(side="left", fill="x", expand=True)

        divider_text = ctk.CTkLabel(divider_frame, text="OR", font=ctk.CTkFont(size=12))
        divider_text.pack(side="left", padx=10)

        divider_line2 = ctk.CTkFrame(divider_frame, height=1, fg_color="gray")
        divider_line2.pack(side="left", fill="x", expand=True)

        # Register button
        self.register_btn = ctk.CTkButton(
            button_frame,
            text="Create New Account",
            command=self.show_register_window,
            height=45,
            font=ctk.CTkFont(size=16),
            corner_radius=10,
            fg_color="transparent",
            border_width=2
        )
        self.register_btn.pack(fill="x", padx=30, pady=(10, 0))

    def _create_status_section(self):
        """Create status display section"""
        self.status_frame = ctk.CTkFrame(self.main_frame, corner_radius=10, height=80)
        self.status_frame.pack(fill="x", pady=(0, 15), padx=30)
        self.status_frame.pack_propagate(False)  # Maintain fixed height

        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready to sign in",
            font=ctk.CTkFont(size=12),
            text_color="white",
            wraplength=350
        )
        self.status_label.pack(expand=True, pady=10)

    def _create_footer(self):
        """Create footer section"""
        footer_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        footer_frame.pack(side="bottom", fill="x")

        footer_label = ctk.CTkLabel(
            footer_frame,
            text="© 2024 Argus Authentication System",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        footer_label.pack(pady=10)

    def _toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.show_password_var.get():
            self.password.configure(show="")
        else:
            self.password.configure(show="*")

    def _validate_inputs(self, login_id, password):
        """Validate user inputs"""
        errors = []

        # Check if fields are empty
        if not login_id.strip():
            errors.append("Login ID is required")

        if not password.strip():
            errors.append("Password is required")

        # Basic login ID validation (can be customized based on requirements)
        if login_id.strip() and len(login_id.strip()) < 3:
            errors.append("Login ID must be at least 3 characters long")

        # Basic password validation
        if password.strip() and len(password.strip()) < 6:
            errors.append("Password must be at least 6 characters long")

        return errors

    def _show_status(self, message, color="red", duration=None):
        """Display status message with optional auto-clear"""
        self.status_label.configure(text=message, text_color=color)

        if duration:
            self.root.after(duration, lambda: self.status_label.configure(text="Ready to sign in", text_color="gray"))

    def _set_loading_state(self, is_loading):
        """Set loading state for UI elements"""
        self.is_logging_in = is_loading

        if is_loading:
            self.login_btn.configure(text="Signing In...", state="disabled")
            self.register_btn.configure(state="disabled")
            self.login_id.configure(state="disabled")
            self.password.configure(state="disabled")
        else:
            self.login_btn.configure(text="Sign In", state="normal")
            self.register_btn.configure(state="normal")
            self.login_id.configure(state="normal")
            self.password.configure(state="normal")

    def login(self):
        """Handle login process with improved error handling"""
        if self.is_logging_in:
            return

        try:
            # Get input values
            login_id = self.login_id.get().strip()
            password = self.password.get().strip()

            # Validate inputs
            validation_errors = self._validate_inputs(login_id, password)
            if validation_errors:
                self._show_status("\n".join(validation_errors), "red")
                return None

            # Set loading state
            self._set_loading_state(True)
            self._show_status("Authenticating...", "#1f538d")

            # Make API call
            response = AuthAPI.login(login_id, password)

            if response.get("success"):
                # Success case
                employee_data = response.get("employee", {})
                username = employee_data.get("name", "User")
                user_id_num = employee_data.get("id")

                if not user_id_num:
                    raise Exception("Invalid response: User ID not found")

                self._show_status(f"Welcome back, {username}! 🎉", "green")

                # Delay before opening main window
                self.root.after(1500, lambda: self.safe_destroy_and_open_main(user_id_num, username))
                return employee_data

            else:
                # Handle API failure
                error_message = response.get("message", "Login failed. Please check your credentials.")
                self._show_status(f"❌ {error_message}", "red")
                self._set_loading_state(False)
                return None

        except Exception as e:
            # Handle exceptions
            error_msg = str(e)
            if "connection" in error_msg.lower():
                self._show_status("❌ Connection error. Please check your internet connection.", "red")
            elif "timeout" in error_msg.lower():
                self._show_status("❌ Request timeout. Please try again.", "red")
            else:
                self._show_status(f"❌ Error: {error_msg}", "red")

            self._set_loading_state(False)

            # Log the exception for debugging
            print(f"Login error: {e}")
            raise CustomException(e, sys)

    def safe_destroy_and_open_main(self, user_id_num, username):
        """Safely destroy current window and open main application"""
        try:
            if self.root.winfo_exists():
                self.root.destroy()
                self.open_main_window(user_id_num=user_id_num, user_name=username)
        except Exception as e:
            print(f"Error opening main window: {e}")
            # Optionally show error dialog or recreate login window

    def open_main_window(self, user_id_num, user_name):
        """Open the main application window"""
        try:
            app = MainAppUI(user_id_num=str(user_id_num), username=user_name)
            app.run()
        except Exception as e:
            print(f"Error initializing main application: {e}")
            # Could implement fallback or error dialog here

    def show_register_window(self):
        """Show registration window"""
        try:
            RegisterWindow(self.root)
        except Exception as e:
            self._show_status(f"❌ Error opening registration: {str(e)}", "red")
            print(f"Registration window error: {e}")

    def quit(self):
        """Properly quit the application"""
        try:
            if hasattr(self, 'root') and self.root.winfo_exists():
                self.root.quit()
                self.root.destroy()
        except Exception as e:
            print(f"Error during quit: {e}")
        finally:
            sys.exit(0)

    def run(self):
        """Start the application main loop"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("Application interrupted by user")
            self.quit()
        except Exception as e:
            print(f"Application error: {e}")
            self.quit()