import mss
from datetime import datetime
import os
from typing import Optional

from project_config import PROJECT_ROOT

def capture_screenshot() -> Optional[str]:
    """
    Captures a screenshot and saves it to a dated folder within the screenshots directory.
    Returns the path where the screenshot was saved, or None if failed.
    """
    try:
        # Create screenshots directory with timestamp
        timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        screenshot_dir = os.path.join(PROJECT_ROOT, "screenshots", datetime.now().strftime('%Y_%m_%d'))
        os.makedirs(screenshot_dir, exist_ok=True)

        # Generate filename and full path
        filename = f"screenshot_{timestamp}.png"
        full_path = os.path.join(screenshot_dir, filename)

        # Capture and save screenshot
        with mss.mss() as sct:
            sct.shot(output=full_path)

        with open(full_path, 'a'):
            os.utime(full_path, None)

        print(f"Screenshot successfully saved to: {full_path}")
        return full_path

    except Exception as e:
        print(f"Error capturing screenshot: {str(e)}")
        return None


class Capture:
    pass


# # Example usage
# if __name__ == "__main__":
#     screenshot_path = capture_screenshot()
