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


class MemberEditDialog(QDialog):
    def __init__(self, user_id: int, current_phone: str, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.current_phone = current_phone
        self._build_ui()

    def _build_ui(self):
        self.setWindowTitle(M.MEMBER_EDIT_TITLE)
        self.setMinimumSize(400, 260)

        root = QVBoxLayout(self)
        root.setSpacing(16)
        root.setContentsMargins(24, 24, 24, 24)

        # ── 헤더 ─────────────────────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(48)
        header.setStyleSheet(f"background-color: {theme.HEADER_BG}; border-radius: 12px;")
        header_row = QHBoxLayout(header)
        header_row.setContentsMargins(16, 0, 16, 0)

        lbl = QLabel("회원정보 수정")
        h_font = QFont()
        h_font.setPointSize(12)
        h_font.setBold(True)
        lbl.setFont(h_font)
        lbl.setStyleSheet(f"color: {theme.HEADER_TEXT};")
        header_row.addWidget(lbl)
        header_row.addStretch()
        root.addWidget(header)

        # ── 폼 ───────────────────────────────────────────────────────────
        form_card = QFrame()
        form_card.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.SURFACE};
                border: none;
                border-radius: 12px;
            }}
        """)
        form = QFormLayout(form_card)
        form.setVerticalSpacing(12)
        form.setHorizontalSpacing(12)
        form.setContentsMargins(18, 16, 18, 16)
        form.setLabelAlignment(Qt.AlignLeft)

        self._phone = QLineEdit(self.current_phone)
        self._phone.setPlaceholderText("010-0000-0000")
        self._phone.setFixedHeight(38)
        form.addRow(M.MEMBER_EDIT_PHONE, self._phone)

        root.addWidget(form_card)

        # ── 버튼 ─────────────────────────────────────────────────────────
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        ok_btn = buttons.button(QDialogButtonBox.Ok)
        ok_btn.setText(M.MEMBER_EDIT_BTN_OK)
        ok_btn.setProperty("role", "primary")

        cancel_btn = buttons.button(QDialogButtonBox.Cancel)
        cancel_btn.setText(M.BTN_CANCEL)
        cancel_btn.setProperty("role", "danger")

        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    def _on_accept(self):
        phone = self._phone.text().strip()
        if not phone:
            QMessageBox.warning(self, M.ERR_TITLE, "전화번호를 입력해 주세요.")
            return
        try:
            card_service.update_user_phone(self.user_id, phone)
            self.accept()
        except (GiftCardError, ValueError) as e:
            QMessageBox.warning(self, M.ERR_TITLE, str(e))
