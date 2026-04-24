import os
import sys

from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QGuiApplication, QIcon, QPixmap

_STYLE_NORMAL = """
    QPushButton {
        background-color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 0;
    }
"""
_STYLE_HOVER = """
    QPushButton {
        background-color: #f0f0f0;
        border: none;
        border-radius: 8px;
        padding: 0;
    }
"""
_STYLE_PRESSED = """
    QPushButton {
        background-color: #e0e0e0;
        border: none;
        border-radius: 8px;
        padding: 0;
    }
"""


class FloatingReturnButton(QWidget):
    """항상 화면 위에 떠 있는 복귀 버튼 창 (드래그로 위치 이동 가능)."""

    restore_requested = pyqtSignal()

    _LOGO_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "img", "logo.png")
    _SIZE = 60
    _DRAG_THRESHOLD = 5
    _MACOS_FLOATING_LEVEL = 3

    def __init__(self):
        super().__init__()
        self._drag_start = None   # 마우스 누른 시점 전역 좌표
        self._drag_origin = None  # 마우스 누른 시점 위젯 좌표
        self._is_dragging = False

        self.setWindowFlags(
            Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.FramelessWindowHint
        )
        self.setFixedSize(self._SIZE, self._SIZE)
        self.setCursor(Qt.PointingHandCursor)

        self._btn = QPushButton(self)
        self._btn.setFixedSize(self._SIZE, self._SIZE)
        # 마우스 이벤트를 버튼이 가로채지 않고 부모 위젯으로 전달
        self._btn.setAttribute(Qt.WA_TransparentForMouseEvents)

        pix = QPixmap(self._LOGO_PATH)
        if not pix.isNull():
            self._btn.setIcon(QIcon(pix))
            self._btn.setIconSize(self._btn.size())
            self._btn.setText("")
        else:
            self._btn.setText("복귀")

        self._btn.setStyleSheet(_STYLE_NORMAL)
        self._reposition()

    # ── 마우스 이벤트 (부모 위젯이 직접 처리) ──────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start = event.globalPos()
            self._drag_origin = self.pos()
            self._is_dragging = False
            self._btn.setStyleSheet(_STYLE_PRESSED)
            self.setCursor(Qt.SizeAllCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_start is not None and (event.buttons() & Qt.LeftButton):
            delta = event.globalPos() - self._drag_start
            if not self._is_dragging:
                if abs(delta.x()) > self._DRAG_THRESHOLD or abs(delta.y()) > self._DRAG_THRESHOLD:
                    self._is_dragging = True
            if self._is_dragging:
                self.move(self._drag_origin + delta)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.PointingHandCursor)
            self._btn.setStyleSheet(_STYLE_HOVER)
            if not self._is_dragging:
                self.restore_requested.emit()
            # 상태 초기화 (드래그 여부와 무관하게 항상 리셋)
            self._drag_start = None
            self._drag_origin = None
            self._is_dragging = False
        super().mouseReleaseEvent(event)

    def enterEvent(self, event):
        self._btn.setStyleSheet(_STYLE_HOVER)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._btn.setStyleSheet(_STYLE_NORMAL)
        super().leaveEvent(event)

    # ── 창 표시 / macOS 설정 ───────────────────────────────────────────────

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

            sel_hides = objc.sel_registerName(b"setHidesOnDeactivate:")
            send.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_bool]
            send(nswindow, sel_hides, False)
        except Exception:
            pass

    def _reposition(self):
        """초기 위치: 화면 왼쪽 아래."""
        screen = QGuiApplication.primaryScreen().availableGeometry()
        margin = 20
        self.move(
            screen.left() + margin,
            screen.bottom() - self.height() - margin,
        )
