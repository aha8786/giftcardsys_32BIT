import os

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLineEdit, QDialogButtonBox, QMessageBox, QLabel, QFrame, QWidget,
    QCheckBox, QPushButton, QScrollArea, QApplication,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from src.ui import messages as M
from src.ui import theme
from src.service import card_service
from src.exceptions import GiftCardError
from src.paths import resource_path

_DEFAULT_NAME  = "홍길동"
_DEFAULT_PHONE = "01000000000"
_CHECKMARK_IMG = resource_path("img/checkmark_white.png").replace("\\", "/")

# 숫자패드 패널 치수 — 첫 화면에서 전체가 보이도록 비율 축소
_NP_BTN_W  = 54     # 버튼 너비 (62 → 54)
_NP_BTN_H  = 46     # 버튼 높이 (56 → 46)
_NP_GAP    = 5      # 버튼 간격 (6 → 5)
_NP_PAD    = 10     # 패널 좌우 여백 (12 → 10)
# 패널 전체 너비 = (버튼 3개 + 간격 2개 + 좌우 여백)
_NP_W      = _NP_BTN_W * 3 + _NP_GAP * 2 + _NP_PAD * 2   # 192px (222 → 192)

_FORM_W    = 400    # 왼쪽 폼 고정 너비 (440 → 400)


class CardRegisterDialog(QDialog):
    def __init__(self, barcode="", parent=None):
        # type: (str, object) -> None
        super().__init__(parent)
        self.barcode = barcode
        self.result_data = None  # type: ignore
        self._build_ui()

    def _build_ui(self):
        self.setWindowTitle(M.REGISTER_TITLE)
        # 작은 화면에서 다이얼로그가 작업표시줄/타이틀바에 가려지지 않도록 최대 높이 제한
        # GIFTCARD_FAKE_SCREEN_H 환경변수로 작은 화면 시뮬레이션 가능 (테스트용)
        fake_h = int(os.environ.get("GIFTCARD_FAKE_SCREEN_H", "0") or "0")
        if fake_h > 0:
            avail_h = fake_h
        else:
            screen = QApplication.primaryScreen()
            avail_h = screen.availableGeometry().height() if screen is not None else 1080
        max_h = max(340, avail_h - 80)
        self.setMaximumHeight(max_h)
        # 첫 화면에서 컨텐츠(약 495px)가 잘리지 않도록 minimum을 충분히 크게.
        # 화면이 작으면 max_h가 minimum을 잘라 작아지고, 그때만 ScrollArea가 활성화된다.
        self.setMinimumHeight(min(500, max_h))

        # 최상위 레이아웃: 왼쪽 폼 + 오른쪽 숫자패드(토글) — 둘 다 ScrollArea로 감싸 작은 화면 대응
        outer = QHBoxLayout(self)
        outer.setSpacing(0)
        outer.setContentsMargins(0, 0, 0, 0)

        # ── 왼쪽 폼 패널 (ScrollArea로 감쌈) ─────────────────────────────
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setFrameShape(QScrollArea.NoFrame)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        left_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        left_scroll.setFixedWidth(_FORM_W)
        outer.addWidget(left_scroll)

        left_panel = QWidget()
        left_scroll.setWidget(left_panel)
        root = QVBoxLayout(left_panel)
        root.setSpacing(10)               # 14 → 10
        root.setContentsMargins(18, 16, 18, 16)  # 24,24,24,24 → 18,16,18,16

        # 헤더
        header = QFrame()
        header.setFixedHeight(46)         # 56 → 46
        header.setStyleSheet(
            "QFrame {{ background-color: {bg}; border: none; border-radius: 14px; }}".format(
                bg=theme.BRIGHT
            )
        )
        header.setGraphicsEffect(theme.card_shadow(blur=16, opacity=0.10))
        header_row = QHBoxLayout(header)
        header_row.setContentsMargins(20, 0, 20, 0)

        accent_dot = QLabel("●")
        accent_dot.setStyleSheet(
            "color: {}; font-size: 16px;".format(theme.PRIMARY_BTN)
        )
        header_row.addWidget(accent_dot)

        lbl_h = QLabel("신규 회원 등록")
        h_font = QFont()
        h_font.setPointSize(12)           # 13 → 12
        h_font.setBold(True)
        lbl_h.setFont(h_font)
        lbl_h.setStyleSheet("color: #ffffff; font-weight: 800;")
        header_row.addWidget(lbl_h)
        header_row.addStretch()
        root.addWidget(header)

        lbl_sub = QLabel("등록할 회원의 정보를 입력해 주세요.")
        lbl_sub.setAlignment(Qt.AlignCenter)
        lbl_sub.setStyleSheet("color: {}; font-size: 12px;".format(theme.MUTED))
        root.addWidget(lbl_sub)

        # 폼 카드
        form_card = QFrame()
        form_card.setStyleSheet(
            "QFrame {{ background-color: {bg}; border: 1.5px solid {bd};"
            " border-radius: 14px; }}".format(bg=theme.SURFACE, bd=theme.BORDER)
        )
        form_card.setGraphicsEffect(theme.card_shadow(blur=12, opacity=0.04))
        form = QFormLayout(form_card)
        form.setRowWrapPolicy(QFormLayout.WrapAllRows)
        form.setVerticalSpacing(8)        # 12 → 8
        form.setHorizontalSpacing(10)     # 12 → 10
        form.setContentsMargins(16, 14, 16, 14)  # 20,18,20,18 → 16,14,16,14
        form.setLabelAlignment(Qt.AlignLeft)

        # 바코드
        self._barcode_input = QLineEdit(self.barcode)
        self._barcode_input.setPlaceholderText("바코드 번호")
        self._barcode_input.setFixedHeight(34)  # 40 → 34
        form.addRow("바코드", self._barcode_input)

        # 이름 + 기본값 체크박스
        name_container = QWidget()
        name_container.setStyleSheet("background: transparent;")
        name_row = QHBoxLayout(name_container)
        name_row.setContentsMargins(0, 0, 0, 0)
        name_row.setSpacing(8)

        self._name = QLineEdit(_DEFAULT_NAME)
        self._name.setPlaceholderText("이름 입력")
        self._name.setFixedHeight(34)     # 40 → 34
        self._name.setEnabled(False)
        self._name.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                color: #0a0a0a;
                border: 1.5px solid #e0e0e0;
                border-radius: 10px;
                padding: 8px 14px;
            }
            QLineEdit:disabled {
                background-color: #d1d5db;
                color: #6b7280;
                border-color: #c4c9d0;
            }
            QLineEdit:focus {
                border-color: #0a0a0a;
            }
        """)
        name_row.addWidget(self._name, stretch=1)

        self._name_default_cb = QCheckBox("기본값 입력")
        self._name_default_cb.setChecked(True)
        self._name_default_cb.setStyleSheet("""
            QCheckBox {{
                color: #166534;
                font-size: 12px;
                font-weight: 600;
                spacing: 6px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid #22c55e;
                border-radius: 4px;
                background-color: #ffffff;
            }}
            QCheckBox::indicator:checked {{
                background-color: #22c55e;
                border-color: #16a34a;
                image: url("{checkmark}");
            }}
            QCheckBox::indicator:unchecked {{
                background-color: #ffffff;
                border-color: #22c55e;
            }}
            QCheckBox::indicator:hover {{
                border-color: #16a34a;
            }}
        """.format(checkmark=_CHECKMARK_IMG))
        self._name_default_cb.stateChanged.connect(self._on_name_default_changed)
        name_row.addWidget(self._name_default_cb)
        form.addRow(M.REGISTER_NAME_LABEL, name_container)

        # 전화번호 + 기본값 체크박스
        phone_container = QWidget()
        phone_container.setStyleSheet("background: transparent;")
        phone_row = QHBoxLayout(phone_container)
        phone_row.setContentsMargins(0, 0, 0, 0)
        phone_row.setSpacing(8)

        self._phone = QLineEdit(_DEFAULT_PHONE)
        self._phone.setPlaceholderText("010-0000-0000")
        self._phone.setFixedHeight(34)    # 40 → 34
        self._phone.setEnabled(False)
        self._phone.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                color: #0a0a0a;
                border: 1.5px solid #e0e0e0;
                border-radius: 10px;
                padding: 8px 14px;
            }
            QLineEdit:disabled {
                background-color: #d1d5db;
                color: #6b7280;
                border-color: #c4c9d0;
            }
            QLineEdit:focus {
                border-color: #0a0a0a;
            }
        """)
        phone_row.addWidget(self._phone, stretch=1)

        self._phone_default_cb = QCheckBox("기본값 입력")
        self._phone_default_cb.setChecked(True)
        self._phone_default_cb.setStyleSheet("""
            QCheckBox {{
                color: #166534;
                font-size: 12px;
                font-weight: 600;
                spacing: 6px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid #22c55e;
                border-radius: 4px;
                background-color: #ffffff;
            }}
            QCheckBox::indicator:checked {{
                background-color: #22c55e;
                border-color: #16a34a;
                image: url("{checkmark}");
            }}
            QCheckBox::indicator:unchecked {{
                background-color: #ffffff;
                border-color: #22c55e;
            }}
            QCheckBox::indicator:hover {{
                border-color: #16a34a;
            }}
        """.format(checkmark=_CHECKMARK_IMG))
        self._phone_default_cb.stateChanged.connect(self._on_phone_default_changed)
        phone_row.addWidget(self._phone_default_cb)
        form.addRow(M.REGISTER_PHONE_LABEL, phone_container)

        # 초기 충전 금액 + 키보드 아이콘 토글 버튼
        amount_container = QWidget()
        amount_container.setStyleSheet("background: transparent;")
        amount_row = QHBoxLayout(amount_container)
        amount_row.setContentsMargins(0, 0, 0, 0)
        amount_row.setSpacing(4)

        self._amount = QLineEdit()
        self._amount.setPlaceholderText("0")
        self._amount.setFixedHeight(34)   # 40 → 34
        self._amount.textChanged.connect(self._format_amount)
        amount_row.addWidget(self._amount, stretch=1)

        self._kb_btn = QPushButton("⌨")
        self._kb_btn.setFixedSize(34, 34) # 40,40 → 34,34
        self._kb_btn.setToolTip("숫자패드 열기/닫기")
        self._kb_btn.setCheckable(True)
        self._kb_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #444444;
                border: 1.5px solid #e0e0e0;
                border-radius: 8px;
                font-size: 18px;
                padding: 0;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
                border-color: #bbbbbb;
            }
            QPushButton:pressed {
                background-color: #d5d5d5;
            }
            QPushButton:checked {
                background-color: #c5e12b;
                border-color: #a8be1a;
                color: #0a0a0a;
            }
        """)
        self._kb_btn.toggled.connect(self._toggle_numpad)
        amount_row.addWidget(self._kb_btn)

        form.addRow(M.REGISTER_INITIAL_LABEL, amount_container)
        root.addWidget(form_card)

        # 확인 / 취소 버튼
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        ok_btn = buttons.button(QDialogButtonBox.Ok)
        ok_btn.setText(M.REGISTER_BTN_OK)
        ok_btn.setProperty("role", "primary")

        cancel_btn = buttons.button(QDialogButtonBox.Cancel)
        cancel_btn.setText(M.REGISTER_BTN_CANCEL)

        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

        # ── 오른쪽 숫자패드 패널 (초기 숨김, ScrollArea 안에) ─────────────────
        self._numpad_panel = self._make_numpad_panel()
        self._numpad_scroll = QScrollArea()
        self._numpad_scroll.setWidgetResizable(True)
        self._numpad_scroll.setFrameShape(QScrollArea.NoFrame)
        self._numpad_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._numpad_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._numpad_scroll.setFixedWidth(_NP_W)
        self._numpad_scroll.setWidget(self._numpad_panel)
        self._numpad_scroll.setVisible(False)
        outer.addWidget(self._numpad_scroll)

    # ── 숫자패드 패널 생성 ─────────────────────────────────────────────────

    def _make_numpad_panel(self):
        panel = QFrame()
        panel.setFixedWidth(_NP_W)
        panel.setStyleSheet(
            "QFrame {{ background-color: {bg}; border-left: 1.5px solid {bd}; }}".format(
                bg=theme.SURFACE_MID, bd=theme.BORDER
            )
        )

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(_NP_PAD, 16, _NP_PAD, 16)  # 24 → 16
        layout.setSpacing(8)              # 10 → 8

        lbl = QLabel("초기 충전 금액")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(
            "color: {c}; font-size: 10px; font-weight: 700;"
            " letter-spacing: 1px; background: transparent;".format(c=theme.MUTED)
        )
        layout.addWidget(lbl)

        grid = QGridLayout()
        grid.setSpacing(_NP_GAP)
        grid.setContentsMargins(0, 0, 0, 0)

        num_font = QFont()
        num_font.setPointSize(14)
        num_font.setBold(True)

        keys = [
            ("7", 0, 0), ("8", 0, 1), ("9", 0, 2),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2),
            ("1", 2, 0), ("2", 2, 1), ("3", 2, 2),
            ("00", 3, 0), ("0", 3, 1), ("C", 3, 2),
        ]
        for label, row, col in keys:
            btn = QPushButton(label)
            btn.setFixedSize(_NP_BTN_W, _NP_BTN_H)
            btn.setFont(num_font)
            btn.setProperty("role", "numpad-clear" if label == "C" else "numpad")
            btn.clicked.connect(lambda checked, k=label: self._on_numpad_key(k))
            grid.addWidget(btn, row, col)

        layout.addLayout(grid)
        layout.addStretch()
        return panel

    # ── 슬롯 ─────────────────────────────────────────────────────────────

    def _toggle_numpad(self, checked):
        self._numpad_scroll.setVisible(checked)
        self.adjustSize()

    def _on_numpad_key(self, key):
        raw = self._amount.text().replace(",", "")
        if key == "C":
            self._amount.clear()
        elif key == "00":
            if raw and raw != "0":
                self._amount.setText(raw + "00")
        else:
            if raw == "0":
                self._amount.setText(key)
            else:
                self._amount.setText(raw + key)

    def _on_name_default_changed(self, state):
        if state == Qt.Checked:
            self._name.setText(_DEFAULT_NAME)
            self._name.setEnabled(False)
        else:
            self._name.clear()
            self._name.setEnabled(True)
            self._name.setFocus()

    def _on_phone_default_changed(self, state):
        if state == Qt.Checked:
            self._phone.setText(_DEFAULT_PHONE)
            self._phone.setEnabled(False)
        else:
            self._phone.clear()
            self._phone.setEnabled(True)
            self._phone.setFocus()

    def _format_amount(self, text):
        # type: (str) -> None
        digits = "".join(c for c in text if c.isdigit())
        formatted = "{:,}".format(int(digits)) if digits else ""
        if formatted != text:
            self._amount.blockSignals(True)
            cursor = self._amount.cursorPosition()
            self._amount.setText(formatted)
            diff = len(formatted) - len(text)
            self._amount.setCursorPosition(max(0, cursor + diff))
            self._amount.blockSignals(False)

    def _on_accept(self):
        barcode = self._barcode_input.text().strip()
        name = self._name.text().strip()
        phone = self._phone.text().strip()
        if not barcode:
            QMessageBox.warning(self, M.ERR_TITLE, "바코드를 입력해 주세요.")
            return
        if not name:
            QMessageBox.warning(self, M.ERR_TITLE, "이름을 입력해 주세요.")
            return
        if not phone:
            QMessageBox.warning(self, M.ERR_TITLE, "전화번호를 입력해 주세요.")
            return
        digits = self._amount.text().replace(",", "")
        amount = int(digits) if digits else 0
        try:
            self.result_data = card_service.register(barcode, phone, name, amount)
            self.barcode = barcode
            self.accept()
        except GiftCardError as e:
            QMessageBox.warning(self, M.ERR_TITLE, str(e))
