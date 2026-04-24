from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QFrame, QAbstractItemView,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from src.ui import messages as M
from src.ui import theme
from src.ui.transaction_dialog import TransactionDialog
from src.service import card_service
from src.exceptions import GiftCardError
from config import settings


class CardInfoWindow(QWidget):
    transaction_done = pyqtSignal()

    def __init__(self, info: dict, notifiers: list, parent=None):
        super().__init__(parent)
        self.notifiers = notifiers
        self._info = info
        self.setWindowTitle(M.CARD_INFO_TITLE)
        self.setMinimumSize(760, 600)
        self._build_ui()
        self._load(info)

    def _notify(self, event: str, context: dict) -> None:
        for n in self.notifiers:
            try:
                n.notify(event, context)
            except Exception:
                pass

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(12)
        root.setContentsMargins(20, 20, 20, 20)

        # ── 헤더 ────────────────────────────────────────────────────────────
        header = QFrame()
        header.setFixedHeight(56)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.SURFACE};
                border: none;
                border-radius: 14px;
            }}
        """)
        header.setGraphicsEffect(theme.card_shadow(blur=16, opacity=0.05))
        header_row = QHBoxLayout(header)
        header_row.setContentsMargins(20, 0, 20, 0)

        lbl_title = QLabel(M.CARD_INFO_TITLE)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        lbl_title.setFont(title_font)
        lbl_title.setStyleSheet(f"color: {theme.BRIGHT}; font-weight: 800;")
        header_row.addWidget(lbl_title)
        header_row.addStretch()

        self._btn_member_info = QPushButton(M.BTN_MEMBER_INFO)
        self._btn_member_info.setFixedSize(130, 38)
        self._btn_member_info.clicked.connect(self._on_open_member_search)
        header_row.addWidget(self._btn_member_info)
        root.addWidget(header)

        # ── 히어로 잔액 카드 ────────────────────────────────────────────────
        balance_card = QFrame()
        balance_card.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.BRIGHT};
                border-radius: 16px;
            }}
        """)
        balance_card.setFixedHeight(116)
        balance_card.setGraphicsEffect(theme.card_shadow(blur=28, y=6, opacity=0.14))
        balance_inner = QHBoxLayout(balance_card)
        balance_inner.setContentsMargins(28, 20, 28, 20)

        balance_left = QVBoxLayout()
        lbl_bal_title = QLabel("현재 잔액")
        lbl_bal_title.setStyleSheet(
            "color: rgba(255,255,255,0.5); font-size: 11px; font-weight: 700; letter-spacing: 1px;"
        )
        balance_left.addWidget(lbl_bal_title)

        self._lbl_balance = QLabel("0 원")
        bal_font = QFont()
        bal_font.setPointSize(34)
        bal_font.setBold(True)
        self._lbl_balance.setFont(bal_font)
        self._lbl_balance.setStyleSheet("color: #ffffff;")
        balance_left.addWidget(self._lbl_balance)
        balance_inner.addLayout(balance_left, stretch=1)

        balance_right = QVBoxLayout()
        balance_right.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        balance_right.setSpacing(12)

        self._btn_charge = QPushButton(M.BTN_CHARGE)
        self._btn_charge.setFixedSize(120, 44)
        self._btn_charge.setProperty("role", "charge")
        self._btn_charge.clicked.connect(lambda: self._on_transaction("charge"))
        balance_right.addWidget(self._btn_charge)

        self._btn_pay = QPushButton(M.BTN_PAY)
        self._btn_pay.setFixedSize(120, 44)
        self._btn_pay.setProperty("role", "pay")
        self._btn_pay.clicked.connect(lambda: self._on_transaction("pay"))
        balance_right.addWidget(self._btn_pay)
        balance_inner.addLayout(balance_right)
        root.addWidget(balance_card)

        # ── 회원 정보 카드 행 ────────────────────────────────────────────────
        info_row = QHBoxLayout()
        info_row.setSpacing(10)

        self._lbl_barcode = self._make_info_card("회원코드", "", theme.PRIMARY_LIGHT, theme.BRIGHT)
        self._lbl_phone   = self._make_info_card("전화번호", "", theme.SURFACE_MID, theme.BODY)

        info_row.addWidget(self._lbl_barcode[0], stretch=1)
        info_row.addWidget(self._lbl_phone[0],   stretch=1)
        root.addLayout(info_row)

        # ── 거래 내역 ──────────────────────────────────────────────────────
        hist_card = QFrame()
        hist_card.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.SURFACE};
                border: none;
                border-radius: 14px;
            }}
        """)
        hist_card.setGraphicsEffect(theme.card_shadow(blur=16, opacity=0.05))
        hist_outer = QVBoxLayout(hist_card)
        hist_outer.setContentsMargins(0, 0, 0, 0)
        hist_outer.setSpacing(0)

        hist_header = QWidget()
        hist_header.setFixedHeight(50)
        hist_header.setStyleSheet(f"""
            QWidget {{
                background-color: {theme.SURFACE};
                border-top-left-radius: 14px;
                border-top-right-radius: 14px;
            }}
        """)
        hist_header_row = QHBoxLayout(hist_header)
        hist_header_row.setContentsMargins(20, 0, 20, 0)

        lbl_hist = QLabel("거래 내역")
        lbl_hist_font = QFont()
        lbl_hist_font.setPointSize(12)
        lbl_hist_font.setBold(True)
        lbl_hist.setFont(lbl_hist_font)
        lbl_hist.setStyleSheet(f"color: {theme.BRIGHT}; font-weight: 800;")
        hist_header_row.addWidget(lbl_hist)
        hist_header_row.addStretch()
        hist_outer.addWidget(hist_header)

        # 구분선
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {theme.BORDER};")
        hist_outer.addWidget(sep)

        self._table = QTableWidget(0, len(M.TX_TABLE_HEADERS))
        self._table.setHorizontalHeaderLabels(M.TX_TABLE_HEADERS)
        hdr = self._table.horizontalHeader()
        hdr.setSectionResizeMode(QHeaderView.Stretch)
        for col in (0, 1, 2, 5):  # 번호·구분·카드ID·일시는 내용 너비에 맞게
            hdr.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setAlternatingRowColors(False)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(True)
        self._table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._table.setStyleSheet(f"""
            QTableWidget {{ border: none; border-bottom-left-radius: 14px; border-bottom-right-radius: 14px; }}
            QTableWidget::item {{ padding: 11px 14px; border: none; }}
            QTableWidget::item:selected {{ background-color: {theme.PRIMARY_LIGHT}; color: {theme.BRIGHT}; }}
        """)
        hist_outer.addWidget(self._table)
        root.addWidget(hist_card, stretch=1)

    def _make_info_card(self, title: str, value: str, bg: str, fg: str):
        frame = QFrame()
        frame.setFixedHeight(80)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: 1.5px solid {theme.BORDER};
                border-radius: 12px;
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(4)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(
            f"color: {theme.MUTED}; font-size: 10px; font-weight: 700; letter-spacing: 0.8px; border: none;"
        )
        layout.addWidget(lbl_title)

        lbl_value = QLabel(value)
        val_font = QFont()
        val_font.setPointSize(14)
        val_font.setBold(True)
        lbl_value.setFont(val_font)
        lbl_value.setStyleSheet(f"color: {fg}; border: none;")
        layout.addWidget(lbl_value)

        return frame, lbl_value

    def _load(self, info: dict):
        self._info = info
        card = info["card"]
        user = info["user"]

        self._lbl_barcode[1].setText(card["barcode"])
        self._lbl_phone[1].setText(user["phone_number"])
        self._lbl_balance.setText(f"{card['balance']:,} 원")

        txs = info["transactions"]
        self._table.setRowCount(len(txs))
        for row, tx in enumerate(txs):
            tx_type = tx["type"]
            for col, val in enumerate([
                tx["id"], theme.tx_label(tx["type"]), tx["card_id"],
                f"{tx['amount']:,}", f"{tx['balance_after']:,}", tx["created_at"],
            ]):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                theme.style_tx_item(item, tx_type)
                self._table.setItem(row, col, item)

    def _refresh(self):
        try:
            info = card_service.lookup(self._info["card"]["barcode"])
            self._load(info)
        except GiftCardError as e:
            QMessageBox.warning(self, M.ERR_TITLE, str(e))

    def _on_transaction(self, mode: str):
        card = self._info["card"]
        user = self._info["user"]
        dlg = TransactionDialog(mode, card["barcode"], card["balance"], self)
        if dlg.exec_() and dlg.result_data:
            data = dlg.result_data
            self._refresh()
            self.transaction_done.emit()
            event = "charged" if mode == "charge" else "paid"
            self._notify(event, {
                "barcode": card["barcode"],
                "amount": data["amount"],
                "balance": data["balance"],
                "phone_number": user["phone_number"],
            })
            if data["balance"] < settings.LOW_BALANCE_THRESHOLD:
                self._notify("low_balance", {
                    "balance": data["balance"],
                    "phone_number": user["phone_number"],
                })

    def _on_open_member_search(self):
        from src.ui.member_search import MemberSearchPanel
        panel = MemberSearchPanel(self)
        panel.setWindowFlag(Qt.Window)
        panel.transaction_done.connect(self._refresh)
        panel.show()
