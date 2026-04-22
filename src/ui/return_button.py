import os
import sys

from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QGuiApplication, QIcon, QPixmap


class FloatingReturnButton(QWidget):
    """항상 화면 위에 떠 있는 복귀 버튼 창."""

    restore_requested = pyqtSignal()

    _LOGO_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "img", "logo.png")
    _SIZE = 60

    # macOS NSFloatingWindowLevel — 모든 일반 앱 창보다 위
    _MACOS_FLOATING_LEVEL = 3

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.FramelessWindowHint
        )
        self.setFixedSize(self._SIZE, self._SIZE)

        btn = QPushButton(self)
        btn.setFixedSize(self._SIZE, self._SIZE)
        btn.setCursor(Qt.PointingHandCursor)

        pix = QPixmap(self._LOGO_PATH)
        if not pix.isNull():
            btn.setIcon(QIcon(pix))
            btn.setIconSize(btn.size())
            btn.setText("")
        else:
            btn.setText("복귀")

        btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: none;
                border-radius: 8px;
                padding: 0;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
        """)
        btn.clicked.connect(self.restore_requested)

        self._reposition()

    def showEvent(self, event):
        super().showEvent(event)
        if sys.platform == "darwin":
            self._macos_force_floating()

    def _macos_force_floating(self):
        """macOS에서 다른 앱 창보다도 항상 위에 뜨도록 NSWindow 레벨을 직접 설정."""
        try:
            import ctypes
            import ctypes.util

            objc = ctypes.cdll.LoadLibrary(ctypes.util.find_library("objc"))
            objc.sel_registerName.restype = ctypes.c_void_p
            objc.sel_registerName.argtypes = [ctypes.c_char_p]

            sel_window = objc.sel_registerName(b"window")
            sel_set_level = objc.sel_registerName(b"setLevel:")

            nsview = ctypes.c_void_p(int(self.winId()))

            send = objc.objc_msgSend
            send.restype = ctypes.c_void_p
            send.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
            nswindow = send(nsview, sel_window)

            send.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_long]
            send(nswindow, sel_set_level, self._MACOS_FLOATING_LEVEL)

            # 앱이 비활성화돼도 버튼이 숨겨지지 않도록 설정
            sel_hides = objc.sel_registerName(b"setHidesOnDeactivate:")
            send.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_bool]
            send(nswindow, sel_hides, False)
        except Exception:
            pass

    def _reposition(self):
        screen = QGuiApplication.primaryScreen().availableGeometry()
        margin = 20
        self.move(
            screen.right() - self.width() - margin,
            screen.bottom() - self.height() - margin,
        )
