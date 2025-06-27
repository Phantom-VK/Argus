import re
import customtkinter as ctk
from src.argus.api.auth import AuthAPI
from src.argus.exceptions import CustomException


class RegisterWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Register New Account")
        self.geometry("400x480")
        self.parent = parent

        # Form Fields
        self.name_entry = ctk.CTkEntry(self, placeholder_text="Full Name")
        self.email_entry = ctk.CTkEntry(self, placeholder_text="Email")
        self.mobile_entry = ctk.CTkEntry(self, placeholder_text="Mobile Number")
        self.login_id_entry = ctk.CTkEntry(self, placeholder_text="Login ID")
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.confirm_pass_entry = ctk.CTkEntry(self, placeholder_text="Confirm Password", show="*")

        # Buttons
        self.register_btn = ctk.CTkButton(self, text="Register", state="normal", command=self.register_user)
        self.cancel_btn = ctk.CTkButton(self, text="Cancel", state="normal", command=self.destroy)

        # Status Label
        self.status_label = ctk.CTkLabel(self, text="", text_color="red")

        # Setup Layout
        self._setup_layout()

        # Modal
        self.transient(parent)
        self.after(10, self.grab_set)

    def _setup_layout(self):
        ctk.CTkLabel(self, text="Create New Account", font=("Arial", 16)).pack(pady=12)

        self.name_entry.pack(pady=6, padx=20, fill="x")
        self.email_entry.pack(pady=6, padx=20, fill="x")
        self.mobile_entry.pack(pady=6, padx=20, fill="x")
        self.login_id_entry.pack(pady=6, padx=20, fill="x")
        self.password_entry.pack(pady=6, padx=20, fill="x")
        self.confirm_pass_entry.pack(pady=6, padx=20, fill="x")

        self.status_label.pack(pady=6)

        self.register_btn.pack(pady=10, padx=40, fill="x")
        self.cancel_btn.pack(pady=4, padx=40, fill="x")

    def register_user(self):
        # Get data
        username = self.name_entry.get()
        email = self.email_entry.get()
        mobile = self.mobile_entry.get()
        login_id = self.login_id_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_pass_entry.get()

        # Password match check
        if password != confirm_password:
            self.status_label.configure(text="Passwords do not match.", text_color="red")
            return

        # Validate fields
        valid, message = self._validate_registration_fields(username, email, mobile, login_id, password)
        if not valid:
            self.status_label.configure(text=message, text_color="red")
            return

        try:
            # Construct user data
            user_data = {
                "company_id": 1,
                "name": username,
                "email": email,
                "mobile": mobile,
                "login_id": login_id,
                "password": password
            }

            response = AuthAPI.register(user_data)

            if response.get("success"):
                self.status_label.configure(text="Registration successful!", text_color="green")
                self.after(1500, self.destroy)
            else:
                raise CustomException(response.get("message", "Registration failed."))

        except CustomException as e:
            self.status_label.configure(text=str(e), text_color="red")

    def _validate_registration_fields(self, username, email, mobile, login_id, password):
        if not all([username.strip(), email.strip(), mobile.strip(), login_id.strip(), password.strip()]):
            return False, "All fields are required."

        if len(username) < 2:
            return False, "Username is too short."

        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            return False, "Invalid email format."

        if not (mobile.isdigit() and len(mobile) == 10):
            return False, "Mobile number must be 10 digits."

        if len(login_id) < 4:
            return False, "Login ID must be at least 4 characters long."

        if len(password) < 6:
            return False, "Password should be at least 6 characters."
        if not any(c.isupper() for c in password):
            return False, "Password must have an uppercase letter."
        if not any(c.islower() for c in password):
            return False, "Password must have a lowercase letter."
        if not any(c.isdigit() for c in password):
            return False, "Password must include a number."

        return True, "Valid"
