import os
import platform
from appdirs import user_data_dir
from datetime import datetime


class FileManager:
    def __init__(self, app_name="Argus"):
        self.app_name = app_name
        self.base_dir = self._get_base_dir()

    def _get_base_dir(self) -> str:
        """Returns OS-appropriate application data directory"""
        if platform.system() == "Windows":
            # Windows: C:\Users\<user>\AppData\Local\Argus
            return user_data_dir(self.app_name, roaming=False)
        elif platform.system() == "Darwin":
            # Mac: ~/Library/Application Support/Argus
            return user_data_dir(self.app_name)
        else:
            # Linux: ~/.local/share/Argus
            return user_data_dir(self.app_name)

    def get_path(self, *subdirs, create=True) -> str:
        """
        Get path to subdirectory in app data folder
        Args:
            *subdirs: path components (e.g., "screenshots", "2023")
            create: whether to create directory if it doesn't exist
        Returns:
            Full absolute path
        """
        path = os.path.join(self.base_dir, *subdirs)
        if create:
            os.makedirs(path, exist_ok=True)
        return path

    def get_screenshot_path(self, user_id: str) -> str:
        """Get dated screenshot path for today"""
        today = datetime.now().strftime("%Y-%m-%d-%H")
        return self.get_path("screenshots", user_id, today)

    def get_log_path(self) -> str:
        """Get path for log files"""
        return self.get_path("logs")


# Singleton instance
file_manager = FileManager()