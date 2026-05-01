from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QMessageBox, QLabel, QFrame, QWidget, QHBoxLayout,
    QPushButton, QInputDialog,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from src.ui import messages as M
from src.ui import theme
from src.service import card_service
from src.exceptions import GiftCardError

_DELETE_PASSWORD = "0000"


class MemberEditDialog(QDialog):
    def __init__(self, user_id, current_phone, current_name="", parent=None):
        # type: (int, str, str, object) -> None
        super().__init__(parent)
        self.user_id = user_id
        self.current_phone = current_phone
        self.current_name = current_name
        self.deleted = False
        self._build_ui()

    def _build_ui(self):
        self.setWindowTitle(M.MEMBER_EDIT_TITLE)
        self.setMinimumSize(400, 280)

        root = QVBoxLayout(self)
        root.setSpacing(16)
        root.setContentsMargins(24, 24, 24, 24)

        # ── 헤더 ─────────────────────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(48)
        header.setStyleSheet(
            "background-color: {}; border-radius: 12px;".format(theme.HEADER_BG)
        )
        header_row = QHBoxLayout(header)
        header_row.setContentsMargins(16, 0, 16, 0)

        lbl = QLabel("회원정보 수정")
        h_font = QFont()
        h_font.setPointSize(12)
        h_font.setBold(True)
        lbl.setFont(h_font)
        lbl.setStyleSheet("color: {};".format(theme.HEADER_TEXT))
        header_row.addWidget(lbl)
        header_row.addStretch()
        root.addWidget(header)

        # ── 폼 ───────────────────────────────────────────────────────────
        form_card = QFrame()
        form_card.setStyleSheet(
            "QFrame {{ background-color: {bg}; border: none; border-radius: 12px; }}".format(
                bg=theme.SURFACE
            )
        )
        form = QFormLayout(form_card)
        form.setVerticalSpacing(12)
        form.setHorizontalSpacing(12)
        form.setContentsMargins(18, 16, 18, 16)
        form.setLabelAlignment(Qt.AlignLeft)

        self._name = QLineEdit(self.current_name)
        self._name.setPlaceholderText("이름 입력")
        self._name.setFixedHeight(38)
        form.addRow(M.MEMBER_EDIT_NAME, self._name)

        self._phone = QLineEdit(self.current_phone)
        self._phone.setPlaceholderText("010-0000-0000")
        self._phone.setFixedHeight(38)
        form.addRow(M.MEMBER_EDIT_PHONE, self._phone)

        root.addWidget(form_card)

        # ── 버튼 행 ───────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        btn_delete = QPushButton(M.MEMBER_DELETE_BTN)
        btn_delete.setFixedHeight(38)
        btn_delete.setMinimumWidth(90)
        btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #ef4444;
                border: 2px solid #ef4444;
                border-radius: 999px;
                font-size: 13px;
                font-weight: 700;
                padding: 0 16px;
            }
            QPushButton:hover {
                background-color: #fee2e2;
                border-color: #dc2626;
                color: #dc2626;
            }
            QPushButton:pressed {
                background-color: #fecaca;
                border-color: #b91c1c;
            }
        """)
        btn_delete.clicked.connect(self._on_delete)
        btn_row.addWidget(btn_delete)

        btn_row.addStretch()

        btn_cancel = QPushButton(M.BTN_CANCEL)
        btn_cancel.setFixedHeight(38)
        btn_cancel.setMinimumWidth(72)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)

        btn_ok = QPushButton(M.MEMBER_EDIT_BTN_OK)
        btn_ok.setFixedHeight(38)
        btn_ok.setMinimumWidth(72)
        btn_ok.setProperty("role", "primary")
        btn_ok.clicked.connect(self._on_accept)
        btn_row.addWidget(btn_ok)

        root.addLayout(btn_row)

    # ── 슬롯 ─────────────────────────────────────────────────────────────

    def _on_accept(self):
        name = self._name.text().strip()
        phone = self._phone.text().strip()
        if not phone:
            QMessageBox.warning(self, M.ERR_TITLE, "전화번호를 입력해 주세요.")
            return
        if not name:
            QMessageBox.warning(self, M.ERR_TITLE, "이름을 입력해 주세요.")
            return
        try:
            card_service.update_user(self.user_id, phone, name)
            self.accept()
        except (GiftCardError, ValueError) as e:
            QMessageBox.warning(self, M.ERR_TITLE, str(e))

    def _on_delete(self):
        # 1단계: 비밀번호 확인
        text, ok = QInputDialog.getText(
            self,
            M.MEMBER_DELETE_PW_TITLE,
            M.MEMBER_DELETE_PW_LABEL,
            QLineEdit.Password,
        )
        if not ok:
            return
        if text != _DELETE_PASSWORD:
            QMessageBox.warning(self, M.ERR_TITLE, M.MEMBER_DELETE_PW_WRONG)
            return

        # 2단계: 최종 확인
        reply = QMessageBox.question(
            self,
            M.MEMBER_DELETE_CONFIRM_TITLE,
            M.MEMBER_DELETE_CONFIRM_MSG,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        # 3단계: 삭제 실행
        try:
            card_service.delete_member(self.user_id)
            self.deleted = True
            QMessageBox.information(self, "완료", M.MEMBER_DELETE_SUCCESS)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, M.ERR_TITLE, str(e))
