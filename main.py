import sys

from PyQt5.QtWidgets import QApplication, QMessageBox

from config import settings
from src.db import connection as db_conn
from src.db.schema import init_db
from src.exceptions import DatabaseConnectionError
from src.notifications.logger import LogNotifier, configure_logger
from src.notifications.popup import PopupNotifier
from src.notifications.kakao import KakaoNotifier
from src.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("기프트카드 관리 시스템")

    from src.ui.theme import apply as apply_theme
    apply_theme(app)

    try:
        db_conn.configure(settings.DB_PATH)
        init_db()
    except DatabaseConnectionError as e:
        QMessageBox.critical(None, "DB 오류", str(e))
        sys.exit(1)

    configure_logger(settings.LOG_PATH)
    notifiers = [PopupNotifier(), LogNotifier(), KakaoNotifier()]

    window = MainWindow(notifiers)
    window.show()
    _setup_global_hotkey(window)
    sys.exit(app.exec_())


def _setup_global_hotkey(window) -> None:
    try:
        import keyboard
        from PyQt5.QtCore import QMetaObject, Qt

        def _callback():
            QMetaObject.invokeMethod(window, "restore_window", Qt.QueuedConnection)

        keyboard.add_hotkey("ctrl+alt+a", _callback)
    except Exception:
        pass


if __name__ == "__main__":
    main()
