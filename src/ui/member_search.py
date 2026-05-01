from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QFrame, QAbstractItemView,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from src.ui import messages as M
from src.ui import theme
from src.service import card_service

_CHARGE_BTN_STYLE = """
    QPushButton {
        background-color: #00de5a;
        color: #ffffff;
        border: none;
        border-radius: 13px;
        font-size: 13px;
        font-weight: 900;
        padding: 0;
    }
    QPushButton:hover  { background-color: #00c450; }
    QPushButton:pressed { background-color: #00a844; }
"""

_PAY_BTN_STYLE = """
    QPushButton {
        background-color: #ff0000;
        color: #ffffff;
        border: none;
        border-radius: 13px;
        font-size: 13px;
        font-weight: 900;
        padding: 0;
    }
    QPushButton:hover  { background-color: #e60000; }
    QPushButton:pressed { background-color: #cc0000; }
"""


class MemberSearchPanel(QWidget):
    transaction_done = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(M.MEMBER_SEARCH_TITLE)
        self.setMinimumSize(820, 540)
        self._rows_data: list = []
        self._build_ui()
        self._on_search()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        # ── 헤더 ─────────────────────────────────────────────────────────
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

        accent_dot = QLabel("●")
        accent_dot.setStyleSheet(f"color: {theme.PRIMARY_BTN}; font-size: 16px;")
        header_row.addWidget(accent_dot)

        lbl_title = QLabel("회원 검색")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        lbl_title.setFont(title_font)
        lbl_title.setStyleSheet(f"color: {theme.BRIGHT}; font-weight: 800;")
        header_row.addWidget(lbl_title)
        header_row.addStretch()
        layout.addWidget(header)

        # ── 검색 바 ───────────────────────────────────────────────────────
        search_card = QFrame()
        search_card.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.SURFACE};
                border: none;
                border-radius: 12px;
            }}
        """)
        search_card.setGraphicsEffect(theme.card_shadow(blur=16, opacity=0.05))
        search_outer = QVBoxLayout(search_card)
        search_outer.setContentsMargins(16, 14, 16, 14)

        search_row = QHBoxLayout()
        search_row.setSpacing(8)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText(M.MEMBER_SEARCH_PLACEHOLDER)
        self._search_input.setFixedHeight(42)
        self._search_input.returnPressed.connect(self._on_search)
        search_row.addWidget(self._search_input, stretch=1)

        btn_search = QPushButton(M.MEMBER_BTN_SEARCH)
        btn_search.setProperty("role", "primary")
        btn_search.setFixedSize(84, 42)
        btn_search.clicked.connect(self._on_search)
        search_row.addWidget(btn_search)
        search_outer.addLayout(search_row)
        layout.addWidget(search_card)

        # ── 회원 목록 테이블 ───────────────────────────────────────────────
        table_card = QFrame()
        table_card.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.SURFACE};
                border: none;
                border-radius: 14px;
            }}
        """)
        table_card.setGraphicsEffect(theme.card_shadow(blur=20, opacity=0.06))
        table_outer = QVBoxLayout(table_card)
        table_outer.setContentsMargins(0, 0, 0, 0)
        table_outer.setSpacing(0)

        table_header_w = QWidget()
        table_header_w.setFixedHeight(50)
        table_header_w.setStyleSheet(f"""
            QWidget {{
                background-color: {theme.SURFACE};
                border-top-left-radius: 14px;
                border-top-right-radius: 14px;
            }}
        """)
        table_header_row = QHBoxLayout(table_header_w)
        table_header_row.setContentsMargins(20, 0, 20, 0)

        lbl_list = QLabel("회원 목록")
        lbl_list_font = QFont()
        lbl_list_font.setPointSize(12)
        lbl_list_font.setBold(True)
        lbl_list.setFont(lbl_list_font)
        lbl_list.setStyleSheet(f"color: {theme.BRIGHT}; font-weight: 800;")
        table_header_row.addWidget(lbl_list)
        table_header_row.addStretch()

        hint = QLabel("더블클릭 → 정보 수정")
        hint.setStyleSheet(f"color: {theme.MUTED}; font-size: 11px;")
        table_header_row.addWidget(hint)
        table_outer.addWidget(table_header_w)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {theme.BORDER};")
        table_outer.addWidget(sep)

        self._table = QTableWidget(0, len(M.MEMBER_LIST_HEADERS))
        self._table.setHorizontalHeaderLabels(M.MEMBER_LIST_HEADERS)

        hdr = self._table.horizontalHeader()
        hdr.setSectionResizeMode(QHeaderView.Stretch)
        # 잔액·등록일·액션은 내용 너비 고정, 나머지(이름·전화번호·바코드)가 남은 공간을 채움
        hdr.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 잔액
        hdr.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 등록일
        hdr.setSectionResizeMode(5, QHeaderView.Fixed)             # 액션 버튼
        self._table.setColumnWidth(5, 132)

        self._table.verticalHeader().setDefaultSectionSize(52)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(True)
        self._table.setStyleSheet(
            "QTableWidget { border: none; border-bottom-left-radius: 14px;"
            " border-bottom-right-radius: 14px; }"
        )
        self._table.cellDoubleClicked.connect(self._on_row_double_click)
        table_outer.addWidget(self._table)
        layout.addWidget(table_card, stretch=1)

    # ── 버튼 셀 위젯 ─────────────────────────────────────────────────────

    def _make_action_cell(self, row_idx: int) -> QWidget:
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        hbox = QHBoxLayout(container)
        hbox.setContentsMargins(4, 3, 4, 3)
        hbox.setSpacing(6)
        hbox.addStretch()

        btn_charge = QPushButton("▲")
        btn_charge.setFixedSize(30, 26)
        btn_charge.setStyleSheet(_CHARGE_BTN_STYLE)
        btn_charge.clicked.connect(lambda _, i=row_idx: self._open_transaction(i, "charge"))
        hbox.addWidget(btn_charge)

        btn_pay = QPushButton("▼")
        btn_pay.setFixedSize(30, 26)
        btn_pay.setStyleSheet(_PAY_BTN_STYLE)
        btn_pay.clicked.connect(lambda _, i=row_idx: self._open_transaction(i, "pay"))
        hbox.addWidget(btn_pay)

        hbox.addStretch()
        return container

    # ── 슬롯 ─────────────────────────────────────────────────────────────

    def _on_search(self):
        keyword = self._search_input.text().strip()
        rows = card_service.search_users(keyword)
        self._rows_data = rows
        self._table.setRowCount(len(rows))

        for r, row in enumerate(rows):
            for c, val in enumerate([
                row.get("name", ""),
                row.get("phone_number", ""),
                row.get("barcode", ""),
                "{:,} 원".format(row.get("balance", 0)) if row.get("balance") is not None else "",
                row.get("created_at", ""),
            ]):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                self._table.setItem(r, c, item)

            self._table.setCellWidget(r, 5, self._make_action_cell(r))

        if keyword and not rows:
            QMessageBox.information(self, M.MEMBER_SEARCH_TITLE, M.MEMBER_NO_RESULT)

    def _open_transaction(self, row_idx, mode):
        # type: (int, str) -> None
        if row_idx >= len(self._rows_data):
            return
        data = self._rows_data[row_idx]
        barcode = data.get("barcode")
        balance = data.get("balance") or 0
        if not barcode:
            QMessageBox.warning(self, M.ERR_TITLE, "카드가 등록되지 않은 회원입니다.")
            return
        from src.ui.transaction_dialog import TransactionDialog
        dlg = TransactionDialog(mode, barcode, balance, self)
        if dlg.exec_() and dlg.result_data:
            result = dlg.result_data
            label = "충전" if mode == "charge" else "결제"
            QMessageBox.information(
                self,
                label + " 완료",
                "{label} 완료\n{amount:,}원 {label}되었습니다.\n현재 잔액: {balance:,}원".format(
                    label=label,
                    amount=result["amount"],
                    balance=result["balance"],
                ),
            )
            self._on_search()
            self.transaction_done.emit()

    def _on_row_double_click(self, row: int, _col: int):
        if row >= len(self._rows_data):
            return
        data = self._rows_data[row]
        from src.ui.member_edit_dialog import MemberEditDialog
        dlg = MemberEditDialog(data["id"], data.get("phone_number", ""), data.get("name", ""), self)
        if dlg.exec_():
            self._on_search()
