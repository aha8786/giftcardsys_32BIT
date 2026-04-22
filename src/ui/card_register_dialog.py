from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QDialogButtonBox, QMessageBox, QLabel, QFrame, QWidget, QHBoxLayout,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from src.ui import messages as M
from src.ui import theme
from src.service import card_service
from src.exceptions import GiftCardError


class CardRegisterDialog(QDialog):
    def __init__(self, barcode: str = "", parent=None):
        super().__init__(parent)
        self.barcode = barcode
        self.result_data: dict | None = None
        self._build_ui()

    def _build_ui(self):
        self.setWindowTitle(M.REGISTER_TITLE)
        self.setMinimumSize(440, 360)

        root = QVBoxLayout(self)
        root.setSpacing(14)
        root.setContentsMargins(24, 24, 24, 24)

        # ── 헤더 ─────────────────────────────────────────────────────────
        header = QFrame()
        header.setFixedHeight(56)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.BRIGHT};
                border: none;
                border-radius: 14px;
            }}
        """)
        header.setGraphicsEffect(theme.card_shadow(blur=16, opacity=0.10))
        header_row = QHBoxLayout(header)
        header_row.setContentsMargins(20, 0, 20, 0)

        accent_dot = QLabel("●")
        accent_dot.setStyleSheet(f"color: {theme.PRIMARY_BTN}; font-size: 16px;")
        header_row.addWidget(accent_dot)

        lbl_h = QLabel("신규 회원 등록")
        h_font = QFont()
        h_font.setPointSize(13)
        h_font.setBold(True)
        lbl_h.setFont(h_font)
        lbl_h.setStyleSheet("color: #ffffff; font-weight: 800;")
        header_row.addWidget(lbl_h)
        header_row.addStretch()
        root.addWidget(header)

        lbl_sub = QLabel("등록할 회원의 정보를 입력해 주세요.")
        lbl_sub.setAlignment(Qt.AlignCenter)
        lbl_sub.setStyleSheet(f"color: {theme.MUTED}; font-size: 12px;")
        root.addWidget(lbl_sub)

        # ── 폼 ───────────────────────────────────────────────────────────
        form_card = QFrame()
        form_card.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.SURFACE};
                border: 1.5px solid {theme.BORDER};
                border-radius: 14px;
            }}
        """)
        form_card.setGraphicsEffect(theme.card_shadow(blur=12, opacity=0.04))
        form = QFormLayout(form_card)
        form.setRowWrapPolicy(QFormLayout.WrapAllRows)
        form.setVerticalSpacing(12)
        form.setHorizontalSpacing(12)
        form.setContentsMargins(20, 18, 20, 18)
        form.setLabelAlignment(Qt.AlignLeft)

        self._barcode_input = QLineEdit(self.barcode)
        self._barcode_input.setPlaceholderText("바코드 번호")
        self._barcode_input.setFixedHeight(40)
        form.addRow("바코드", self._barcode_input)

        self._phone = QLineEdit()
        self._phone.setPlaceholderText("010-0000-0000")
        self._phone.setFixedHeight(40)
        form.addRow(M.REGISTER_PHONE_LABEL, self._phone)

        self._amount = QLineEdit()
        self._amount.setPlaceholderText("0")
        self._amount.setFixedHeight(40)
        self._amount.textChanged.connect(self._format_amount)
        form.addRow(M.REGISTER_INITIAL_LABEL, self._amount)

        root.addWidget(form_card)

        # ── 버튼 ─────────────────────────────────────────────────────────
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        ok_btn = buttons.button(QDialogButtonBox.Ok)
        ok_btn.setText(M.REGISTER_BTN_OK)
        ok_btn.setProperty("role", "primary")

        cancel_btn = buttons.button(QDialogButtonBox.Cancel)
        cancel_btn.setText(M.REGISTER_BTN_CANCEL)

        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    def _format_amount(self, text: str):
        digits = "".join(c for c in text if c.isdigit())
        formatted = f"{int(digits):,}" if digits else ""
        if formatted != text:
            self._amount.blockSignals(True)
            cursor = self._amount.cursorPosition()
            self._amount.setText(formatted)
            # 콤마 추가/제거로 인한 커서 위치 보정
            diff = len(formatted) - len(text)
            self._amount.setCursorPosition(max(0, cursor + diff))
            self._amount.blockSignals(False)

    def _on_accept(self):
        barcode = self._barcode_input.text().strip()
        phone = self._phone.text().strip()
        if not barcode:
            QMessageBox.warning(self, M.ERR_TITLE, "바코드를 입력해 주세요.")
            return
        if not phone:
            QMessageBox.warning(self, M.ERR_TITLE, "전화번호를 입력해 주세요.")
            return
        digits = self._amount.text().replace(",", "")
        amount = int(digits) if digits else 0
        try:
            self.result_data = card_service.register(barcode, phone, amount)
            self.barcode = barcode
            self.accept()
        except GiftCardError as e:
            QMessageBox.warning(self, M.ERR_TITLE, str(e))
