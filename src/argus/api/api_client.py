import sys

import requests
import requests.adapters
import os

from src.argus.exceptions import CustomException
from src.argus.logger import logging

class ActivityTrackerAPI:
    def __init__(self, base_url="https://sggsapp.co.in/etracker"):
        self.base_url = base_url
        self.session = requests.Session()
        self.retry = requests.adapters.HTTPAdapter(max_retries=3)
        self.session.mount('http://', self.retry)
        self.session.mount('https://', self.retry)
        self.session.headers.update({
            "User-Agent": "Argus Productivity Tracker/1.0",
            "Accept": "application/json"
        })

    def upload_activity(self, employee_id: str, screenshot_path: str, work_seconds: int) -> bool:
        """Upload activity data to the API"""
        try:
            if not os.path.exists(screenshot_path):
                logging.error(f"Screenshot file not found: {screenshot_path}")
                return False

            with open(screenshot_path, 'rb') as f:
                response = self.session.post(
                    f"{self.base_url}/store_activity.php",
                    files={'screenshot': f},
                    data={
                        'employee_id': employee_id,
                        'time_between_screenshots_sec': work_seconds,
                        'keyboard_clicks': "0",  # Placeholder
                        'mouse_px_travel': "0",   # Placeholder
                    }
                )

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    logging.info(f"Activity uploaded: {result.get('message')}")
                    return True
                else:
                    logging.error(f"API error: {result.get('message', 'Unknown error')}")
            else:
                logging.error(f"API request failed: {response.status_code} - {response.text}")

        except Exception as e:
            logging.error(f"API communication failed: {str(e)}")
            raise CustomException(e, sys)

        return False

# Singleton instance
api_client = ActivityTrackerAPI()