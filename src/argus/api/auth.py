import sys

import requests
from src.argus.exceptions import CustomException


class AuthAPI:
    BASE_URL = "https://sggsapp.co.in/etracker"

    @classmethod
    def login(cls, login_id: str, password: str) -> dict:
        """Handle user login"""
        try:
            response = requests.post(
                f"{cls.BASE_URL}/login.php",
                json={"login_id": login_id, "password": password},
                timeout=10
            )
            data = response.json()
            if not data.get('success'):
                raise CustomException(data.get('message', 'Login failed'),sys)
            return data
        except requests.exceptions.RequestException as e:
            raise CustomException(f"Network error: {str(e)}", sys)

    @classmethod
    def register(cls, user_data: dict) -> dict:
        """Handle new user registration"""
        try:
            response = requests.post(
                f"{cls.BASE_URL}/register.php",
                json=user_data,
                timeout=10
            )
            data = response.json()
            if not data.get('success'):
                raise CustomException(data.get('message', 'Registration failed'))
            return data
        except requests.exceptions.RequestException as e:
            raise CustomException(f"Network error: {str(e)}", sys)