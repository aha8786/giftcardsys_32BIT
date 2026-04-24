from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QDateEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QMessageBox, QAbstractItemView,
)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QFont

from src.ui import messages as M
from src.ui import theme
from src.service import admin_service, backup_service


class AdminPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(M.ADMIN_TITLE)
        self.setMinimumSize(760, 580)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
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

        lbl_title = QLabel(M.ADMIN_TITLE)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        lbl_title.setFont(title_font)
        lbl_title.setStyleSheet(f"color: {theme.BRIGHT}; font-weight: 800;")
        header_row.addWidget(lbl_title)
        header_row.addStretch()

        btn_backup = QPushButton(M.BACKUP_BTN)
        btn_backup.setFixedSize(90, 34)
        btn_backup.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: #ffffff;
                border: none;
                border-radius: 999px;
                font-size: 12px;
                font-weight: 700;
            }
            QPushButton:hover  { background-color: #1d4ed8; }
            QPushButton:pressed { background-color: #1e40af; }
        """)
        btn_backup.clicked.connect(self._on_backup)
        header_row.addWidget(btn_backup)

        layout.addWidget(header)

        # ── 기간 필터 카드 ─────────────────────────────────────────────────
        filter_card = QFrame()
        filter_card.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.SURFACE};
                border: none;
                border-radius: 14px;
            }}
        """)
        filter_card.setGraphicsEffect(theme.card_shadow(blur=16, opacity=0.05))
        filter_outer = QVBoxLayout(filter_card)
        filter_outer.setContentsMargins(20, 14, 20, 14)
        filter_outer.setSpacing(8)

        filter_lbl = QLabel("기간 선택")
        filter_lbl.setStyleSheet(
            f"color: {theme.MUTED}; font-size: 10px; font-weight: 700; letter-spacing: 1px;"
        )
        filter_outer.addWidget(filter_lbl)

        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)

        def _lbl(text: str) -> QLabel:
            l = QLabel(text)
            l.setStyleSheet(f"color: {theme.SUBTLE}; font-size: 12px; font-weight: 600;")
            return l

        filter_row.addWidget(_lbl(M.ADMIN_START))
        self._start = QDateEdit(QDate.currentDate().addDays(-30))
        self._start.setCalendarPopup(True)
        self._start.setDisplayFormat("yyyy-MM-dd")
        self._start.setFixedSize(130, 36)
        self._start.setMaximumDate(QDate.currentDate())
        filter_row.addWidget(self._start)

        filter_row.addWidget(_lbl(M.ADMIN_END))
        self._end = QDateEdit(QDate.currentDate())
        self._end.setCalendarPopup(True)
        self._end.setDisplayFormat("yyyy-MM-dd")
        self._end.setFixedSize(130, 36)
        self._end.setMaximumDate(QDate.currentDate())
        filter_row.addWidget(self._end)

        btn_search = QPushButton(M.ADMIN_BTN_SEARCH)
        btn_search.setFixedSize(80, 36)
        btn_search.setStyleSheet("""
            QPushButton {
                background-color: #0a0a0a;
                color: #ffffff;
                border: none;
                border-radius: 999px;
                font-weight: 700;
            }
            QPushButton:hover  { background-color: #222222; }
            QPushButton:pressed { background-color: #000000; }
        """)
        btn_search.clicked.connect(self._on_search)
        filter_row.addWidget(btn_search)
        filter_row.addStretch()
        filter_outer.addLayout(filter_row)
        layout.addWidget(filter_card)

        # ── 통계 카드 행 ────────────────────────────────────────────────────
        stats_row = QHBoxLayout()
        stats_row.setSpacing(10)

        self._card_charged = self._make_stat_card(
            M.ADMIN_TOTAL_CHARGED, "0 원",
            theme.WARNING_LIGHT, theme.WARNING_DARK, "▲"
        )
        self._card_used = self._make_stat_card(
            M.ADMIN_TOTAL_USED, "0 원",
            theme.ACCENT_LIGHT, theme.ACCENT_DARK, "▼"
        )
        self._card_balance = self._make_stat_card(
            M.ADMIN_TOTAL_BALANCE, "0 원",
            theme.PRIMARY_LIGHT, theme.BRIGHT, "●"
        )

        for card, _ in (self._card_charged, self._card_used, self._card_balance):
            stats_row.addWidget(card, stretch=1)
        layout.addLayout(stats_row)

        # ── 거래 목록 테이블 ────────────────────────────────────────────────
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

        lbl_list = QLabel("거래 목록")
        lbl_font = QFont()
        lbl_font.setPointSize(12)
        lbl_font.setBold(True)
        lbl_list.setFont(lbl_font)
        lbl_list.setStyleSheet(f"color: {theme.BRIGHT}; font-weight: 800;")
        table_header_row.addWidget(lbl_list)
        table_header_row.addStretch()
        table_outer.addWidget(table_header_w)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {theme.BORDER};")
        table_outer.addWidget(sep)

        self._table = QTableWidget(0, len(M.TX_TABLE_HEADERS))
        self._table.setHorizontalHeaderLabels(M.TX_TABLE_HEADERS)
        hdr = self._table.horizontalHeader()
        hdr.setSectionResizeMode(QHeaderView.Stretch)
        for col in (0, 1, 2, 5):  # 번호·구분·카드ID·일시는 내용 너비에 맞게
            hdr.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
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
        table_outer.addWidget(self._table)
        layout.addWidget(table_card, stretch=1)

        self._on_search()

    def _make_stat_card(self, title: str, value: str, bg: str, fg: str, icon: str):
        frame = QFrame()
        frame.setFixedHeight(100)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: 1.5px solid {theme.BORDER};
                border-radius: 14px;
            }}
        """)
        frame.setGraphicsEffect(theme.card_shadow(blur=14, opacity=0.05))
        vlayout = QVBoxLayout(frame)
        vlayout.setContentsMargins(20, 14, 20, 14)
        vlayout.setSpacing(6)

        title_row = QHBoxLayout()
        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet(f"color: {fg}; font-size: 12px; font-weight: 700; border: none;")
        title_row.addWidget(lbl_icon)
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(
            f"color: {theme.SUBTLE}; font-size: 11px; font-weight: 700; border: none; letter-spacing: 0.5px;"
        )
        title_row.addWidget(lbl_title)
        title_row.addStretch()
        vlayout.addLayout(title_row)

        lbl_value = QLabel(value)
        val_font = QFont()
        val_font.setPointSize(18)
        val_font.setBold(True)
        lbl_value.setFont(val_font)
        lbl_value.setStyleSheet(f"color: {fg}; font-weight: 800; border: none;")
        vlayout.addWidget(lbl_value)

        return frame, lbl_value

    def _on_backup(self):
        try:
            path = backup_service.create_backup()
            QMessageBox.information(
                self,
                M.BACKUP_SUCCESS_TITLE,
                M.BACKUP_SUCCESS_MSG.format(path=path),
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                M.BACKUP_FAIL_TITLE,
                M.BACKUP_FAIL_MSG.format(error=e),
            )

    def _on_search(self):
        start = self._start.date().toString("yyyy-MM-dd")
        end = self._end.date().toString("yyyy-MM-dd")
        data = admin_service.get_stats(start, end)

        self._card_charged[1].setText(f"{data['total_charged']:,} 원")
        self._card_used[1].setText(f"{data['total_used']:,} 원")
        self._card_balance[1].setText(f"{data['total_balance']:,} 원")

        txs = data["transactions"]
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
