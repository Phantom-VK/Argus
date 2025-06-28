from src.argus.ui.main_window import MainAppUI


def open_main_window(user_id_num, user_name):
    app = MainAppUI(user_id_num=str(user_id_num), username=user_name)
    app.run()