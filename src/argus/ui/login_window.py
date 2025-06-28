import sys

import customtkinter as ctk
from src.argus.api.auth import AuthAPI
from src.argus.exceptions import CustomException
from src.argus.ui.register_window import RegisterWindow
from src.argus.utils.utils import open_main_window


class LoginAppUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Argus Authentication")
        self.root.geometry("300x200")

        self._create_widgets()


    def _create_widgets(self):
        self.login_id = ctk.CTkEntry(self.root, placeholder_text="Login ID")
        self.login_id.pack(pady=10)

        self.password = ctk.CTkEntry(self.root, placeholder_text="Password", show="*")
        self.password.pack(pady=5)

        self.login_btn = ctk.CTkButton(self.root, text="Login", command=self.login)
        self.login_btn.pack(pady=5)

        self.register_btn = ctk.CTkButton(self.root, text="Register", command=self.show_register_window)
        self.register_btn.pack(pady=5)

        self.status_label = ctk.CTkLabel(self.root, text="", text_color="red")
        self.status_label.pack()

        # Ensure app closes when window is closed
        self.root.protocol("WM_DELETE_WINDOW", self.quit)


    def login(self):
        try:
            login_id = self.login_id.get()
            password = self.password.get()
            if not login_id or not password:
                self.status_label.configure(text = "Please fill all fields")
                return None
            response = AuthAPI.login(
                login_id,
                password
            )
            if response["success"]:
                self.status_label.configure(text="Login Successful!")
                username = response.get("employee", {}).get("name")
                user_id_num = response.get("employee", {}).get("id")
                self.root.after(1000, lambda: self.safe_destroy_and_open_main(user_id_num, username))
                return response["employee"]
            else:
                self.status_label.configure(text="Failed to login, check your details.")
                return None
        except Exception as e:
            self.status_label.configure(text=str(e))
            raise CustomException(e, sys)

    def safe_destroy_and_open_main(self, user_id_num, username):
        if self.root.winfo_exists():
            self.root.destroy()
            open_main_window(user_id_num=user_id_num, user_name=username)

    def show_register_window(self):
        # Simple registration with minimal fields
        RegisterWindow(self.root)

    def quit(self):
        self.root.quit()

    def run(self):
        self.root.mainloop()


