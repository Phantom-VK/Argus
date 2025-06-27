import sys
import traceback
from src.argus.logger import logging


class CustomException(Exception):
    """Enhanced custom exception with proper traceback handling"""

    def __init__(self, error_message, error_detail=None):
        """
        Args:
            error_message: Descriptive error message
            error_detail: Either sys module or actual exception object
        """
        super().__init__(error_message)
        self.error_message = self._get_error_detail(error_message, error_detail)
        logging.error(self.error_message)

    def _get_error_detail(self, error_message, error_detail):
        """Generate detailed error message with traceback"""
        try:
            if error_detail is None:
                # Case 1: No traceback provided
                return error_message

            if error_detail is sys:
                # Case 2: sys module provided
                exc_type, exc_value, exc_tb = sys.exc_info()
                if exc_tb is None:
                    return error_message
            else:
                # Case 3: Actual exception object provided
                exc_type = type(error_detail)
                exc_value = error_detail
                exc_tb = error_detail.__traceback__

            # Extract traceback details
            tb_list = traceback.extract_tb(exc_tb)
            if not tb_list:
                return error_message

            filename = tb_list[-1].filename
            lineno = tb_list[-1].lineno
            return (
                f"Error occurred in {filename} line {lineno}\n"
                f"Error type: {exc_type.__name__}\n"
                f"Error message: {error_message}"
            )

        except Exception as e:
            # Fallback if something goes wrong in error formatting
            return f"Error: {error_message} (Additional error formatting failed: {str(e)})"

    def __str__(self):
        return self.error_message