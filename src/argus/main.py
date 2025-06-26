import sys
import platform
from src.argus.ui.main_window import AppUI
from src.argus.exceptions import CustomException
from src.argus.logger import logging


def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler using existing logging setup"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # Use your existing logger
    logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    # Try to show GUI error if possible
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Critical Error",
            f"An unexpected error occurred:\n\n{str(exc_value)}\n\nSee logs for details."
        )
        root.destroy()
    except Exception as gui_error:
        logging.warning(f"Failed to show error dialog: {gui_error}")


def check_platform():
    """Platform check that raises your CustomException"""
    current_platform = platform.system()
    supported_platforms = ["Windows", "Darwin", "Linux"]

    if current_platform not in supported_platforms:
        error_msg = f"Unsupported platform: {current_platform}. Supported: {', '.join(supported_platforms)}"
        raise CustomException(error_msg, sys)


def main():
    """Main entry point using existing modules"""
    # Set global exception handler
    sys.excepthook = handle_exception

    # Log startup information using existing logger
    logging.info("Starting Argus application")
    logging.info(f"Platform: {platform.system()} {platform.release()}")
    logging.info(f"Python version: {platform.python_version()}")

    try:
        # Verify platform support
        check_platform()

        # Initialize and run application
        app = AppUI()
        app.run()

    except Exception as e:
        # Let CustomException handle logging if it's our custom exception
        if not isinstance(e, CustomException):
            logging.critical("Application failed", exc_info=True)
        raise
    finally:
        logging.info("Application shutdown completed")
        # Your existing logger will handle shutdown


if __name__ == "__main__":
    main()