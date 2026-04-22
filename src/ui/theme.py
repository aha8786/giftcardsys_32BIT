"""
Craftwork-inspired Clean UI — PyQt5
Light gray background · White card surfaces · Lime-green primary
"""
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QTableWidgetItem
from PyQt5.QtGui import QBrush, QColor

# ── Palette ──────────────────────────────────────────────────────────────────
BASE         = "#ebebeb"   # 밝은 회색 — 창 배경
SURFACE      = "#ffffff"   # 흰색 — 카드 표면
SURFACE_MID  = "#f5f5f5"   # 연한 회색 — 입력 배경
BORDER       = "#e0e0e0"   # 기본 테두리
MUTED        = "#9b9b9b"   # 흐린 텍스트
SUBTLE       = "#666666"   # 보조 텍스트
BODY         = "#333333"   # 본문 텍스트
BRIGHT       = "#0a0a0a"   # 제목 텍스트 (거의 검정)

# Header — Light (다크 헤더 제거)
HEADER_BG    = "#ffffff"
HEADER_TEXT  = "#0a0a0a"
HEADER_SUB   = "#666666"

# Primary — Lime Yellow-Green (포인트 컬러)
PRIMARY      = "#0a0a0a"       # 텍스트용 다크
PRIMARY_DARK = "#222222"
PRIMARY_LIGHT= "#f0fac0"       # 라임 연한 배경
PRIMARY_BTN  = "#c5e12b"       # 라임 버튼 배경

# Charge — Amber (충전)
WARNING      = "#f59e0b"
WARNING_DARK = "#d97706"
WARNING_LIGHT= "#fef3c7"

# Pay — Emerald (결제)
ACCENT       = "#10b981"
ACCENT_DARK  = "#059669"
ACCENT_LIGHT = "#d1fae5"
ACCENT_DIM   = ACCENT_LIGHT

# Danger
DANGER       = "#ef4444"
DANGER_DARK  = "#dc2626"
DANGER_LIGHT = "#fee2e2"

# Info
INFO         = "#3b82f6"
INFO_LIGHT   = "#eff6ff"

# Badge colors — 충전: 초록, 결제: 빨강
CHARGE_FG    = "#166534"
CHARGE_BG    = "#dcfce7"
PAY_FG       = "#991b1b"
PAY_BG       = "#fee2e2"

# ── Gradient stops (레거시 호환 — 일부 코드에서 참조) ─────────────────────────
BTN_PRIMARY_L  = PRIMARY_BTN
BTN_PRIMARY_R  = PRIMARY_BTN
BTN_CHARGE_L   = WARNING
BTN_CHARGE_R   = WARNING_DARK
BTN_PAY_L      = ACCENT
BTN_PAY_R      = ACCENT_DARK
BTN_DANGER_L   = DANGER
BTN_DANGER_R   = DANGER_DARK
BTN_NEUTRAL_L  = SURFACE_MID
BTN_NEUTRAL_R  = SURFACE_MID


# ── Helpers ──────────────────────────────────────────────────────────────────

def card_shadow(blur: int = 20, y: int = 4, opacity: float = 0.07):
    fx = QGraphicsDropShadowEffect()
    fx.setBlurRadius(blur)
    fx.setOffset(0, y)
    fx.setColor(QColor(0, 0, 0, int(255 * opacity)))
    return fx


def tx_label(tx_type: str) -> str:
    """거래 type을 사용자 표시용 라벨로 변환 ('사용' → '결제')."""
    return "결제" if tx_type == "사용" else tx_type


def tx_row_colors(tx_type: str) -> tuple:
    """거래 type에 따른 (배경색, 글자색) 문자열 반환."""
    if tx_type == "충전":
        return CHARGE_BG, CHARGE_FG
    return PAY_BG, PAY_FG


def style_tx_item(item: QTableWidgetItem, tx_type: str) -> None:
    """거래내역 테이블 셀에 type별 배경/글자 색상을 일괄 적용."""
    bg, fg = tx_row_colors(tx_type)
    item.setBackground(QBrush(QColor(bg)))
    item.setForeground(QBrush(QColor(fg)))


# ── Stylesheet ────────────────────────────────────────────────────────────────
STYLESHEET = f"""
/* ── Base ─────────────────────────────────────────────────────────────────── */
QMainWindow, QWidget, QDialog {{
    background-color: {BASE};
    color: {BODY};
    font-family: "Apple SD Gothic Neo", "Malgun Gothic", "나눔고딕",
                 system-ui, -apple-system, sans-serif;
    font-size: 13px;
}}

QLabel {{
    color: {BODY};
    background: transparent;
}}

/* ── QGroupBox ────────────────────────────────────────────────────────────── */
QGroupBox {{
    background-color: {SURFACE};
    border: 1.5px solid {BORDER};
    border-radius: 14px;
    padding: 18px 16px 16px 16px;
    margin-top: 14px;
    font-size: 11px;
    font-weight: 700;
    color: {MUTED};
    letter-spacing: 0.6px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 18px;
    padding: 0 6px;
    background-color: {SURFACE};
    color: {MUTED};
}}

/* ── QLineEdit ────────────────────────────────────────────────────────────── */
QLineEdit {{
    background-color: {SURFACE};
    color: {BRIGHT};
    border: 1.5px solid {BORDER};
    border-radius: 10px;
    padding: 8px 14px;
    selection-background-color: {PRIMARY_BTN};
    selection-color: {BRIGHT};
}}
QLineEdit:focus {{
    border-color: {BRIGHT};
    background-color: {SURFACE};
}}
QLineEdit:hover {{
    border-color: #bbbbbb;
}}
QLineEdit[readOnly="true"] {{
    color: {SUBTLE};
    background-color: {SURFACE_MID};
    border-color: {BORDER};
}}

/* ── QSpinBox / QDateEdit ─────────────────────────────────────────────────── */
QSpinBox, QDateEdit {{
    background-color: {SURFACE};
    color: {BRIGHT};
    border: 1.5px solid {BORDER};
    border-radius: 10px;
    padding: 7px 12px;
    selection-background-color: {PRIMARY_BTN};
}}
QSpinBox:focus, QDateEdit:focus {{
    border-color: {BRIGHT};
}}
QSpinBox:hover, QDateEdit:hover {{
    border-color: #bbbbbb;
}}
QSpinBox::up-button, QSpinBox::down-button {{
    background-color: {SURFACE_MID};
    border: none;
    border-radius: 3px;
    width: 18px;
}}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background-color: {BORDER};
}}
QDateEdit::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 28px;
    border: none;
    background: transparent;
}}

/* ── QPushButton — base ────────────────────────────────────────────────────── */
QPushButton {{
    background-color: {SURFACE};
    color: {BODY};
    border: 1.5px solid {BORDER};
    border-radius: 999px;
    padding: 9px 22px;
    font-size: 13px;
    font-weight: 600;
    outline: none;
}}
QPushButton:hover {{
    background-color: {SURFACE_MID};
    border-color: #bbbbbb;
    color: {BRIGHT};
}}
QPushButton:pressed {{
    background-color: {BORDER};
    border-color: #aaaaaa;
}}
QPushButton:disabled {{
    color: {MUTED};
    background-color: {SURFACE_MID};
    border-color: {BORDER};
}}

/* primary — Lime (포인트 컬러) ────────────────────────────────────────────── */
QPushButton[role="primary"] {{
    background-color: {PRIMARY_BTN};
    color: {BRIGHT};
    border: none;
    font-weight: 700;
    border-radius: 999px;
}}
QPushButton[role="primary"]:hover {{
    background-color: #d4ef3a;
}}
QPushButton[role="primary"]:pressed {{
    background-color: #b0cc1e;
}}

/* charge — Amber (충전) ────────────────────────────────────────────────────── */
QPushButton[role="charge"] {{
    background-color: #ffffff;
    color: {WARNING};
    border: 2px solid {WARNING};
    font-weight: 700;
    border-radius: 999px;
}}
QPushButton[role="charge"]:hover {{
    background-color: {WARNING_LIGHT};
    color: {WARNING_DARK};
    border-color: {WARNING_DARK};
}}
QPushButton[role="charge"]:pressed {{
    background-color: {WARNING_LIGHT};
    color: {WARNING_DARK};
    border-color: {WARNING_DARK};
}}

/* pay — Emerald (결제) ─────────────────────────────────────────────────────── */
QPushButton[role="pay"] {{
    background-color: #ffffff;
    color: {ACCENT};
    border: 2px solid {ACCENT};
    font-weight: 700;
    border-radius: 999px;
}}
QPushButton[role="pay"]:hover {{
    background-color: {ACCENT_LIGHT};
    color: {ACCENT_DARK};
    border-color: {ACCENT_DARK};
}}
QPushButton[role="pay"]:pressed {{
    background-color: {ACCENT_LIGHT};
    color: {ACCENT_DARK};
    border-color: {ACCENT_DARK};
}}

/* danger ────────────────────────────────────────────────────────────────────── */
QPushButton[role="danger"] {{
    background-color: {DANGER};
    color: #ffffff;
    border: none;
    font-weight: 600;
    border-radius: 999px;
}}
QPushButton[role="danger"]:hover {{
    background-color: #f87171;
}}
QPushButton[role="danger"]:pressed {{
    background-color: {DANGER_DARK};
}}

/* numpad ────────────────────────────────────────────────────────────────────── */
QPushButton[role="numpad"] {{
    background-color: {SURFACE};
    color: {BRIGHT};
    border: 1.5px solid {BORDER};
    border-radius: 14px;
    font-size: 20px;
    font-weight: 700;
    padding: 0;
}}
QPushButton[role="numpad"]:hover {{
    background-color: {PRIMARY_BTN};
    border-color: {PRIMARY_BTN};
    color: {BRIGHT};
}}
QPushButton[role="numpad"]:pressed {{
    background-color: #b0cc1e;
    border-color: #b0cc1e;
}}
QPushButton[role="numpad-clear"] {{
    background-color: {DANGER};
    color: #ffffff;
    border: none;
    border-radius: 14px;
    font-size: 16px;
    font-weight: 700;
    padding: 0;
}}
QPushButton[role="numpad-clear"]:hover {{
    background-color: #f87171;
}}
QPushButton[role="numpad-clear"]:pressed {{
    background-color: {DANGER_DARK};
}}

/* ── QTableWidget ─────────────────────────────────────────────────────────── */
QTableWidget {{
    background-color: {SURFACE};
    color: {BODY};
    gridline-color: {BORDER};
    border: none;
    outline: none;
    border-radius: 0;
}}
QTableWidget::item {{
    padding: 11px 14px;
    border: none;
}}
QTableWidget::item:selected {{
    background-color: {PRIMARY_LIGHT};
    color: {BRIGHT};
}}
QHeaderView {{
    background-color: {SURFACE_MID};
}}
QHeaderView::section {{
    background-color: {SURFACE_MID};
    color: {MUTED};
    border: none;
    border-bottom: 1px solid {BORDER};
    padding: 10px 14px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.6px;
    text-transform: uppercase;
}}
QTableCornerButton::section {{
    background-color: {SURFACE_MID};
    border: none;
}}

/* ── QScrollBar ────────────────────────────────────────────────────────────── */
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 0;
    border: none;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 3px;
    min-height: 28px;
}}
QScrollBar::handle:vertical:hover {{
    background: #bbbbbb;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
    background: none;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 6px;
    margin: 0;
    border: none;
}}
QScrollBar::handle:horizontal {{
    background: {BORDER};
    border-radius: 3px;
    min-width: 28px;
}}
QScrollBar::handle:horizontal:hover {{
    background: #bbbbbb;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
    background: none;
}}

/* ── QCalendarWidget ──────────────────────────────────────────────────────── */
QCalendarWidget {{
    background-color: {SURFACE};
    color: {BODY};
}}
QCalendarWidget QToolButton {{
    background-color: {SURFACE_MID};
    color: {BODY};
    border: none;
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 12px;
    font-weight: 600;
}}
QCalendarWidget QToolButton:hover {{
    background-color: {PRIMARY_LIGHT};
    color: {BRIGHT};
}}
QCalendarWidget QMenu {{
    background-color: {SURFACE};
    color: {BODY};
}}
QCalendarWidget QSpinBox {{
    background-color: {SURFACE_MID};
    color: {BODY};
    border: none;
    border-radius: 5px;
}}
QCalendarWidget QAbstractItemView:enabled {{
    background-color: {SURFACE};
    color: {BODY};
    selection-background-color: {PRIMARY_BTN};
    selection-color: {BRIGHT};
}}
QCalendarWidget QAbstractItemView:disabled {{
    color: {MUTED};
}}

/* ── QMessageBox ──────────────────────────────────────────────────────────── */
QMessageBox {{
    background-color: {SURFACE};
    color: {BODY};
}}
QMessageBox QLabel {{
    color: {BODY};
    font-size: 13px;
}}
QMessageBox QPushButton {{
    min-width: 80px;
    min-height: 36px;
}}
QDialogButtonBox QPushButton {{
    min-width: 92px;
    min-height: 38px;
}}

/* ── QToolTip ──────────────────────────────────────────────────────────────── */
QToolTip {{
    background-color: {BRIGHT};
    color: {SURFACE};
    border: none;
    border-radius: 7px;
    padding: 5px 11px;
    font-size: 12px;
}}
"""


def apply(app) -> None:
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)
