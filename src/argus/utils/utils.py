import random
import socket
import customtkinter as ctk

def get_random_interval() -> int:
    return random.randint(60, 120)



def has_internet_connection(timeout=3) -> bool:
    try:
        # Try to connect to Google's DNS server
        socket.create_connection(("8.8.8.8", 53), timeout=timeout)
        return True
    except OSError:
        return False



def show_temp_dialog(parent, title: str = "Notice", message="Processing...", duration=2000):
    def _show():
        dialog = ctk.CTkToplevel(parent)
        dialog.title(title)
        dialog.geometry("320x120")
        dialog.transient(parent)

        label = ctk.CTkLabel(
            dialog,
            text=message,
            font=ctk.CTkFont(size=14),
            wraplength=280,
            justify="center",
            text_color="white"
        )
        label.pack(pady=20, padx=20, fill="both", expand=True)

        # Wait for dialog to be visible, then grab
        dialog.after(10, lambda: dialog.grab_set())
        dialog.after(duration, dialog.destroy)

    # Small delay to let main window settle
    parent.after(100, _show)


def ask_yes_no_dialog(parent, title="Confirmation", message="Are you sure?") -> bool:
    result = {"value": None}

    dialog = ctk.CTkToplevel(parent)
    dialog.title(title)
    dialog.geometry("350x150")
    dialog.transient(parent)
    dialog.grab_set()  # Makes it modal

    label = ctk.CTkLabel(dialog, text=message, wraplength=300, font=ctk.CTkFont(size=14))
    label.pack(pady=(20, 10), padx=20)

    # Button click handlers
    def on_yes():
        result["value"] = True
        dialog.destroy()

    def on_no():
        result["value"] = False
        dialog.destroy()

    # Button layout
    btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    btn_frame.pack(pady=10)

    yes_btn = ctk.CTkButton(btn_frame, text="Yes", command=on_yes, width=100)
    yes_btn.pack(side="left", padx=10)

    no_btn = ctk.CTkButton(btn_frame, text="No", command=on_no, width=100)
    no_btn.pack(side="right", padx=10)

    dialog.wait_window()  # Wait until the dialog is closed
    return result["value"]

