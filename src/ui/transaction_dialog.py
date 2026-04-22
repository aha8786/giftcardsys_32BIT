from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QPushButton, QLabel, QMessageBox, QFrame,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from src.ui import messages as M
from src.ui import theme
from src.service import transaction_service
from src.exceptions import GiftCardError

# 창 너비 기준으로 숫자패드 버튼 크기 계산
# 내부 폭 = 420 - 40(좌우 여백) = 380px
# 버튼 폭 = (380 - 20(간격 2×10)) / 3 = 120px
_W = 420
_PAD = 20          # 좌우 여백
_GAP = 10          # 숫자패드 간격
_BTN_W = (_W - _PAD * 2 - _GAP * 2) // 3   # 120px
_BTN_H = 80


class TransactionDialog(QDialog):
    def __init__(self, mode: str, barcode: str, current_balance: int, parent=None):
        super().__init__(parent)
        assert mode in ("charge", "pay")
        self.mode = mode
        self.barcode = barcode
        self.current_balance = current_balance
        self.result_data: dict | None = None
        self._build_ui()

    def _build_ui(self):
        is_pay = self.mode == "pay"
        self.setWindowTitle(M.CHARGE_TITLE if not is_pay else M.PAY_TITLE)

        # 높이 계산:
        # 타이틀(36) + gap(10) + 잔액카드(90) + gap(10) + 입력(58) + gap(10)
        # + [전액버튼(48) + gap(10)] + 숫자패드(4×80 + 3×10) + gap(10) + 취소(48) + 여백(40)
        numpad_h = 4 * _BTN_H + 3 * _GAP  # 350
        base_h   = 36 + 10 + 90 + 10 + 58 + 10 + numpad_h + 10 + 48 + _PAD * 2
        extra_h  = (48 + 10) if is_pay else 0
        self.setFixedSize(_W, base_h + extra_h)

        root = QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(_PAD, _PAD, _PAD, _PAD)

        # ── 타이틀 ───────────────────────────────────────────────────────
        mode_color = theme.WARNING_DARK if not is_pay else theme.ACCENT_DARK
        lbl_title = QLabel("충전" if not is_pay else "결제")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        lbl_title.setFont(title_font)
        lbl_title.setFixedHeight(36)
        lbl_title.setStyleSheet(f"color: {theme.BRIGHT}; font-weight: 800;")
        root.addWidget(lbl_title)

        # ── 현재 잔액 카드 ────────────────────────────────────────────────
        balance_card = QFrame()
        balance_card.setFixedHeight(90)
        balance_card.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.BRIGHT};
                border: none;
                border-radius: 16px;
            }}
        """)
        balance_card.setGraphicsEffect(theme.card_shadow(blur=20, opacity=0.12))
        balance_layout = QVBoxLayout(balance_card)
        balance_layout.setContentsMargins(24, 14, 24, 14)
        balance_layout.setSpacing(4)

        lbl_bal_title = QLabel("현재 잔액")
        lbl_bal_title.setAlignment(Qt.AlignCenter)
        lbl_bal_title.setStyleSheet(
            "color: rgba(255,255,255,0.45); font-size: 10px; font-weight: 700; letter-spacing: 1.2px;"
        )
        balance_layout.addWidget(lbl_bal_title)

        lbl_balance = QLabel(f"{self.current_balance:,} 원")
        bal_font = QFont()
        bal_font.setPointSize(22)
        bal_font.setBold(True)
        lbl_balance.setFont(bal_font)
        lbl_balance.setAlignment(Qt.AlignCenter)
        lbl_balance.setStyleSheet("color: #ffffff;")
        balance_layout.addWidget(lbl_balance)
        root.addWidget(balance_card)

        # ── 금액 입력 + 확인 버튼 ─────────────────────────────────────────
        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        self._amount_input = QLineEdit()
        self._amount_input.setPlaceholderText("금액 입력")
        self._amount_input.setFixedHeight(58)
        amount_font = QFont()
        amount_font.setPointSize(20)
        amount_font.setBold(True)
        self._amount_input.setFont(amount_font)
        self._amount_input.setAlignment(Qt.AlignRight)
        self._amount_input.returnPressed.connect(self._on_confirm)
        input_row.addWidget(self._amount_input, stretch=1)

        confirm_role = "charge" if not is_pay else "pay"
        btn_confirm = QPushButton(M.BTN_OK)
        btn_confirm.setProperty("role", confirm_role)
        btn_confirm.setFixedSize(88, 58)
        btn_font = QFont()
        btn_font.setPointSize(13)
        btn_font.setBold(True)
        btn_confirm.setFont(btn_font)
        btn_confirm.clicked.connect(self._on_confirm)
        input_row.addWidget(btn_confirm)
        root.addLayout(input_row)

        # ── 전액 버튼 (결제 모드만) ───────────────────────────────────────
        if is_pay:
            btn_full = QPushButton(f"전액  ({self.current_balance:,} 원)")
            btn_full.setFixedHeight(48)
            btn_full.setProperty("role", "pay")
            full_font = QFont()
            full_font.setPointSize(12)
            full_font.setBold(True)
            btn_full.setFont(full_font)
            btn_full.clicked.connect(
                lambda: self._amount_input.setText(f"{self.current_balance:,}")
            )
            root.addWidget(btn_full)

        # ── 숫자 패드 ─────────────────────────────────────────────────────
        grid = QGridLayout()
        grid.setSpacing(_GAP)
        grid.setContentsMargins(0, 0, 0, 0)

        num_font = QFont()
        num_font.setPointSize(18)
        num_font.setBold(True)

        keys = [
            ("7", 0, 0), ("8", 0, 1), ("9", 0, 2),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2),
            ("1", 2, 0), ("2", 2, 1), ("3", 2, 2),
            ("00", 3, 0), ("0", 3, 1), ("C", 3, 2),
        ]
        for label, row, col in keys:
            btn = QPushButton(label)
            btn.setFixedSize(_BTN_W, _BTN_H)
            btn.setFont(num_font)
            btn.setProperty("role", "numpad-clear" if label == "C" else "numpad")
            btn.clicked.connect(lambda checked, k=label: self._on_dial(k))
            grid.addWidget(btn, row, col)

        root.addLayout(grid)

        # ── 취소 버튼 ─────────────────────────────────────────────────────
        btn_cancel = QPushButton(M.BTN_CANCEL)
        btn_cancel.setFixedHeight(48)
        cancel_font = QFont()
        cancel_font.setPointSize(12)
        btn_cancel.setFont(cancel_font)
        btn_cancel.clicked.connect(self.reject)
        root.addWidget(btn_cancel)

    @staticmethod
    def _format(digits: str) -> str:
        return f"{int(digits):,}" if digits else ""

    def _on_dial(self, key: str):
        raw = self._amount_input.text().replace(",", "")
        if key == "C":
            self._amount_input.clear()
        elif key == "00":
            if raw and raw != "0":
                self._amount_input.setText(self._format(raw + "00"))
        else:
            if raw == "0":
                self._amount_input.setText(self._format(key))
            else:
                self._amount_input.setText(self._format(raw + key))

    def _on_confirm(self):
        text = self._amount_input.text().replace(",", "").strip()
        if not text or not text.isdigit():
            QMessageBox.warning(self, M.ERR_TITLE, "올바른 금액을 입력해 주세요.")
            return
        amount = int(text)
        if amount <= 0:
            QMessageBox.warning(self, M.ERR_TITLE, "1원 이상의 금액을 입력해 주세요.")
            return
        try:
            if self.mode == "charge":
                self.result_data = transaction_service.charge(self.barcode, amount)
            else:
                self.result_data = transaction_service.pay(self.barcode, amount)
            self.accept()
        except GiftCardError as e:
            QMessageBox.warning(self, M.ERR_TITLE, str(e))
