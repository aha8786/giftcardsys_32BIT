from datetime import date

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDateEdit,
    QFrame, QSizePolicy, QAbstractItemView,
)
from PyQt5.QtCore import Qt, QDate, QSize, QEvent, pyqtSlot
from PyQt5.QtGui import QFont, QPixmap, QIcon

from src.ui import messages as M
from src.ui import theme
from src.ui.card_register_dialog import CardRegisterDialog
from src.service import card_service
from src.exceptions import CardNotFoundError, GiftCardError
from src.paths import resource_path


class MainWindow(QMainWindow):
    def __init__(self, notifiers: list):
        super().__init__()
        self.notifiers = notifiers
        self.setWindowTitle(M.APP_TITLE)
        # 1366x768 환경(작업표시줄 + 타이틀바 = 약 80px 차감)에서도 들어가도록 높이를 640으로 낮춘다.
        # 거래내역 테이블은 자체 스크롤 가능하므로 화면이 작으면 테이블만 줄어든다.
        self.setMinimumSize(1060, 640)
        self._build_ui()
        self._refresh_list()
        self._return_btn = self._create_return_button()
        self._return_btn.show()

    def _notify(self, event: str, context: dict) -> None:
        for n in self.notifiers:
            try:
                n.notify(event, context)
            except Exception:
                pass

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(10)
        root.setContentsMargins(20, 20, 20, 20)

        # ── Row 1: 상단 헤더 바 (타이틀만) ──────────────────────────────────
        header_card = QFrame()
        header_card.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.SURFACE};
                border: none;
                border-radius: 16px;
            }}
        """)
        header_card.setGraphicsEffect(theme.card_shadow(blur=20, opacity=0.06))
        header_row = QHBoxLayout(header_card)
        header_row.setContentsMargins(18, 12, 18, 12)
        header_row.setSpacing(14)

        lbl_app = QLabel(M.APP_TITLE)
        app_font = QFont()
        app_font.setPointSize(14)
        app_font.setBold(True)
        lbl_app.setFont(app_font)
        lbl_app.setStyleSheet(f"color: {theme.BRIGHT}; font-weight: 800;")
        header_row.addWidget(lbl_app)
        header_row.addStretch()

        root.addWidget(header_card)

        # ── Row 2: 바코드 스캔 카드 ────────────────────────────────────────
        scan_card = QFrame()
        scan_card.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.SURFACE};
                border: none;
                border-radius: 16px;
            }}
        """)
        scan_card.setGraphicsEffect(theme.card_shadow(blur=20, opacity=0.06))
        scan_outer = QVBoxLayout(scan_card)
        scan_outer.setContentsMargins(20, 14, 20, 14)
        scan_outer.setSpacing(6)

        lbl_scan_title = QLabel("바코드 스캔")
        lbl_scan_title.setStyleSheet(
            f"color: {theme.MUTED}; font-size: 10px; font-weight: 700; letter-spacing: 1px;"
        )
        scan_outer.addWidget(lbl_scan_title)

        scan_row = QHBoxLayout()
        scan_row.setSpacing(10)

        self._barcode_input = QLineEdit()
        self._barcode_input.setPlaceholderText(M.BARCODE_PLACEHOLDER)
        self._barcode_input.setFixedHeight(48)
        barcode_font = QFont()
        barcode_font.setPointSize(14)
        barcode_font.setBold(True)
        self._barcode_input.setFont(barcode_font)
        self._barcode_input.returnPressed.connect(self._on_barcode_enter)
        scan_row.addWidget(self._barcode_input, stretch=1)

        btn_scan = QPushButton("스캔")
        btn_scan.setProperty("role", "primary")
        btn_scan.setFixedSize(100, 48)
        btn_scan.setFont(barcode_font)
        btn_scan.clicked.connect(self._on_barcode_enter)
        scan_row.addWidget(btn_scan)

        scan_outer.addLayout(scan_row)
        root.addWidget(scan_card)

        # ── Row 3: 조회 조건 카드 ────────────────────────────────────────
        filter_card = QFrame()
        filter_card.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.SURFACE};
                border: none;
                border-radius: 16px;
            }}
        """)
        filter_card.setGraphicsEffect(theme.card_shadow(blur=16, opacity=0.05))
        filter_outer = QVBoxLayout(filter_card)
        filter_outer.setContentsMargins(20, 14, 20, 14)
        filter_outer.setSpacing(8)

        lbl_filter_title = QLabel("조회 조건")
        lbl_filter_title.setStyleSheet(
            f"color: {theme.MUTED}; font-size: 10px; font-weight: 700; letter-spacing: 1px;"
        )
        filter_outer.addWidget(lbl_filter_title)

        filter_main_row = QHBoxLayout()
        filter_main_row.setSpacing(10)

        # 2×2 입력 그리드
        grid = QGridLayout()
        grid.setSpacing(8)
        grid.setColumnMinimumWidth(1, 150)
        grid.setColumnMinimumWidth(3, 150)

        def _lbl(text: str) -> QLabel:
            l = QLabel(text)
            l.setStyleSheet(f"color: {theme.SUBTLE}; font-size: 12px; font-weight: 600;")
            return l

        self._filter_start = QDateEdit(QDate.currentDate().addDays(-30))
        self._filter_start.setCalendarPopup(True)
        self._filter_start.setDisplayFormat("yyyy-MM-dd")
        self._filter_start.setFixedHeight(36)
        self._filter_start.setMaximumDate(QDate.currentDate())

        self._filter_end = QDateEdit(QDate.currentDate())
        self._filter_end.setCalendarPopup(True)
        self._filter_end.setDisplayFormat("yyyy-MM-dd")
        self._filter_end.setFixedHeight(36)
        self._filter_end.setMaximumDate(QDate.currentDate())

        self._filter_barcode = QLineEdit()
        self._filter_barcode.setPlaceholderText("회원코드")
        self._filter_barcode.setFixedHeight(36)

        self._filter_phone = QLineEdit()
        self._filter_phone.setPlaceholderText("전화번호")
        self._filter_phone.setFixedHeight(36)

        grid.addWidget(_lbl(M.FILTER_PERIOD_START), 0, 0, Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(self._filter_start,           0, 1)
        grid.addWidget(_lbl(M.FILTER_PERIOD_END),    0, 2, Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(self._filter_end,             0, 3)
        grid.addWidget(_lbl(M.FILTER_BARCODE),       1, 0, Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(self._filter_barcode,         1, 1)
        grid.addWidget(_lbl(M.FILTER_PHONE),         1, 2, Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(self._filter_phone,           1, 3)

        filter_main_row.addLayout(grid)

        btn_filter = QPushButton("조회")
        btn_filter.setProperty("role", "primary")
        btn_filter.setFixedSize(76, 80)
        btn_filter_font = QFont()
        btn_filter_font.setPointSize(12)
        btn_filter_font.setBold(True)
        btn_filter.setFont(btn_filter_font)
        btn_filter.clicked.connect(self._refresh_list)
        filter_main_row.addWidget(btn_filter)

        # 구분선
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFixedHeight(70)
        sep.setStyleSheet(f"color: {theme.BORDER};")
        filter_main_row.addWidget(sep, alignment=Qt.AlignVCenter)

        # 액션 버튼 3개 — 그리드 높이에 맞게, 남은 공간을 균등 분할
        ICON_SIZE = QSize(26, 26)

        def _make_nav_btn(img_path: str, label: str) -> QPushButton:
            btn = QPushButton(label)
            btn.setFixedHeight(80)
            btn.setMinimumWidth(90)
            nav_font = QFont()
            nav_font.setPointSize(12)
            nav_font.setBold(True)
            btn.setFont(nav_font)
            pix = QPixmap(img_path)
            if not pix.isNull():
                btn.setIcon(QIcon(pix))
                btn.setIconSize(ICON_SIZE)
            return btn

        btn_member = _make_nav_btn(resource_path("img/회원.png"), "회원")
        btn_member.clicked.connect(self._on_open_member_search)
        filter_main_row.addWidget(btn_member, stretch=1)

        btn_register = _make_nav_btn(resource_path("img/신규.png"), "신규")
        btn_register.clicked.connect(self._on_open_register)
        filter_main_row.addWidget(btn_register, stretch=1)

        btn_admin = _make_nav_btn(resource_path("img/관리자.png"), "관리자")
        btn_admin.clicked.connect(self._on_open_admin)
        filter_main_row.addWidget(btn_admin, stretch=1)

        filter_outer.addLayout(filter_main_row)
        root.addWidget(filter_card)

        # ── Row 4: 거래내역 헤더 ─────────────────────────────────────────
        tx_header_row = QHBoxLayout()
        tx_header_row.setContentsMargins(4, 4, 4, 0)

        lbl_list = QLabel("거래내역")
        lbl_list_font = QFont()
        lbl_list_font.setPointSize(13)
        lbl_list_font.setBold(True)
        lbl_list.setFont(lbl_list_font)
        lbl_list.setStyleSheet(f"color: {theme.BRIGHT}; font-weight: 800;")
        tx_header_row.addWidget(lbl_list)

        self._lbl_count = QLabel("")
        self._lbl_count.setStyleSheet(f"""
            QLabel {{
                color: {theme.SUBTLE};
                background-color: {theme.SURFACE_MID};
                border: 1px solid {theme.BORDER};
                border-radius: 20px;
                font-size: 11px;
                font-weight: 700;
                padding: 2px 12px;
            }}
        """)
        tx_header_row.addWidget(self._lbl_count)
        tx_header_row.addStretch()
        root.addLayout(tx_header_row)

        # ── Row 5: 거래내역 테이블 ────────────────────────────────────────
        table_card = QFrame()
        table_card.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.SURFACE};
                border: none;
                border-radius: 16px;
            }}
        """)
        table_card.setGraphicsEffect(theme.card_shadow(blur=20, opacity=0.06))
        table_outer = QVBoxLayout(table_card)
        table_outer.setContentsMargins(0, 0, 0, 0)
        table_outer.setSpacing(0)

        self._table = QTableWidget(0, len(M.MAIN_LIST_HEADERS))
        self._table.setHorizontalHeaderLabels(M.MAIN_LIST_HEADERS)
        hdr = self._table.horizontalHeader()
        hdr.setSectionResizeMode(QHeaderView.Stretch)
        for col in (0, 1, 2, 7):  # 번호·구분·카드ID·일시는 내용 너비에 맞게
            hdr.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setAlternatingRowColors(False)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(True)
        self._table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._table.setStyleSheet(f"""
            QTableWidget {{
                border: none;
                border-radius: 16px;
            }}
            QTableWidget::item {{
                padding: 11px 14px;
                border: none;
            }}
            QTableWidget::item:selected {{
                background-color: {theme.PRIMARY_LIGHT};
                color: {theme.BRIGHT};
            }}
        """)
        table_outer.addWidget(self._table)
        root.addWidget(table_card, stretch=1)

    # ── slots ──────────────────────────────────────────────────────────────

    def _on_barcode_enter(self):
        barcode = self._barcode_input.text().strip()
        if not barcode:
            return
        self._barcode_input.clear()

        try:
            info = card_service.lookup(barcode)
            self._open_card_info(info)
        except CardNotFoundError:
            dlg = CardRegisterDialog(barcode, self)
            if dlg.exec_() and dlg.result_data:
                info = card_service.lookup(barcode)
                data = dlg.result_data
                phone = info["user"]["phone_number"]
                self._notify("card_registered", {
                    "barcode": barcode,
                    "balance": data["balance"],
                    "phone_number": phone,
                })
                self._open_card_info(info)
            self._refresh_list()
        except GiftCardError as e:
            QMessageBox.warning(self, M.ERR_TITLE, str(e))

    def _open_card_info(self, info: dict):
        from src.ui.card_info_window import CardInfoWindow
        win = CardInfoWindow(info, self.notifiers, self)
        win.setWindowFlag(Qt.Window)
        win.transaction_done.connect(self._refresh_list)
        win.show()

    def _refresh_list(self):
        start = self._filter_start.date().toString("yyyy-MM-dd")
        end = self._filter_end.date().toString("yyyy-MM-dd")
        barcode = self._filter_barcode.text().strip()
        phone = self._filter_phone.text().strip()

        rows = card_service.get_transactions_filtered(start, end, barcode, phone)
        self._table.setRowCount(len(rows))
        self._lbl_count.setText(f"  {len(rows)}건  ")

        for r, tx in enumerate(rows):
            tx_type = tx["type"]
            values = [
                tx["id"], theme.tx_label(tx_type), tx["card_id"], tx["phone_number"],
                tx.get("name", ""),
                "{:,}".format(tx["amount"]), "{:,}".format(tx["balance_after"]), tx["created_at"],
                tx["barcode"],
            ]
            for c, val in enumerate(values):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                theme.style_tx_item(item, tx_type)
                self._table.setItem(r, c, item)

    def _on_open_member_search(self):
        from src.ui.member_search import MemberSearchPanel
        panel = MemberSearchPanel(self)
        panel.setWindowFlag(Qt.Window)
        panel.transaction_done.connect(self._refresh_list)
        panel.show()

    def _on_open_register(self):
        dlg = CardRegisterDialog("", self)
        if dlg.exec_() and dlg.result_data:
            self._refresh_list()

    def _on_open_admin(self):
        try:
            from src.ui.admin_panel import AdminPanel
            panel = AdminPanel(self)
            panel.setWindowFlag(Qt.Window)
            panel.show()
        except Exception as e:
            QMessageBox.critical(self, "오류", f"관리자 화면을 열 수 없습니다.\n\n{e}")

    # ── 최소화 / 복귀 ──────────────────────────────────────────────────────────

    def changeEvent(self, event):
        super().changeEvent(event)
        if (event.type() == QEvent.WindowStateChange
                and self.windowState() & Qt.WindowMinimized):
            self._on_minimize()

    def _on_minimize(self):
        self.hide()

    def _create_return_button(self):
        from src.ui.return_button import FloatingReturnButton
        btn = FloatingReturnButton()
        btn.restore_requested.connect(self.restore_window)
        return btn

    @pyqtSlot()
    def restore_window(self):
        if self.isHidden() or (self.windowState() & Qt.WindowMinimized):
            self.setWindowState(Qt.WindowNoState)
            self.show()
        self.raise_()
        self.activateWindow()

        for child in self.findChildren(QWidget):
            if child.isWindow() and not child.isHidden():
                if child.windowState() & Qt.WindowMinimized:
                    child.setWindowState(Qt.WindowNoState)
                child.raise_()
                child.activateWindow()

    def closeEvent(self, event):
        if self._return_btn is not None:
            self._return_btn.close()
        super().closeEvent(event)
