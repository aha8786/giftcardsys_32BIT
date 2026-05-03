# -*- coding: utf-8 -*-
"""
1366x768 POS 환경 기준 UI 자동 진단 하네스.

실행 시 임시 DB(더미 데이터 포함)를 만들고,
앛/뒤로 주요 화면을 차례로 띄워 텍스트 잘림 / 크기 초과 / 겹침을
검사하고 스크린샷을 저장한다.

결과:
  - tests/diagnostics/screenshots/*.png
  - tests/diagnostics/report.json
"""
import json
import os
import shutil
import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# DB 설정: settings.py가 임포트되기 전에 환경변수를 주입
TMP_DIR = Path(tempfile.mkdtemp(prefix="giftcard_diag_"))
TMP_DB = TMP_DIR / "giftcard_test.db"
os.environ["GIFTCARD_DB_PATH"] = str(TMP_DB)
os.environ["GIFTCARD_LOG_PATH"] = str(TMP_DIR / "giftcard_test.log")
os.environ["GIFTCARD_BACKUP_DIR"] = str(TMP_DIR / "backups")
# 1366x768 작은 화면 시뮬레이션 — 다이얼로그가 자동 축소되는지 검증
os.environ["GIFTCARD_FAKE_SCREEN_H"] = "768"

OUT_DIR = ROOT / "tests" / "diagnostics"
SHOTS_DIR = OUT_DIR / "screenshots"
SHOTS_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = OUT_DIR / "report.json"

TARGET_W = 1366
TARGET_H = 768
TASKBAR_RESERVE = 80  # 소형 POS의 작업표시줄 + 창 제목표줄 여유
USABLE_W = TARGET_W
USABLE_H = TARGET_H - TASKBAR_RESERVE  # 688

REPORT = {
    "target_resolution": "{}x{}".format(TARGET_W, TARGET_H),
    "usable_height": USABLE_H,
    "screens": [],
}


def seed_db():
    """더미 데이터: 회원 30, 카드 30, 거래 200건."""
    if TMP_DB.exists():
        TMP_DB.unlink()
    conn = sqlite3.connect(str(TMP_DB))
    conn.executescript(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT NOT NULL,
            name TEXT NOT NULL DEFAULT '홍길동',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL REFERENCES users(id),
            balance INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_id INTEGER NOT NULL REFERENCES cards(id),
            type TEXT NOT NULL CHECK(type IN ('충전', '사용')),
            amount INTEGER NOT NULL,
            balance_after INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    base_dt = datetime.now() - timedelta(days=20)
    names = ["김성수", "이영희", "박재민", "최서연", "정우진",
             "강민재", "한수희", "조다마스테르", "윤지수", "임재혁",
             "송혁준", "마르티니아이디고레죠", "민지운", "고재귄", "수지세머디텍스",
             "황소윤", "권혁수", "신도희", "노태우", "안우설"]
    for i in range(30):
        name = names[i % len(names)]
        phone = "010{:04d}{:04d}".format(1000 + i, 5000 + i)
        ts = (base_dt + timedelta(days=i // 2, hours=i % 12)).strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            "INSERT INTO users (phone_number, name, created_at) VALUES (?, ?, ?)",
            (phone, name, ts),
        )
        barcode = "880{:010d}".format(100000 + i * 7)
        balance = (i + 1) * 5000
        conn.execute(
            "INSERT INTO cards (barcode, user_id, balance, created_at) VALUES (?, ?, ?, ?)",
            (barcode, i + 1, balance, ts),
        )
    # 거래 내역 200건 (30장 카드에 골고루 분포)
    for n in range(200):
        card_id = (n % 30) + 1
        is_charge = (n % 3) != 0
        amount = ((n * 17) % 9 + 1) * 1000
        type_ = "충전" if is_charge else "사용"
        ts = (base_dt + timedelta(days=n // 6, hours=n % 24)).strftime("%Y-%m-%d %H:%M:%S")
        # balance_after는 대강 어느 정도로 설정 (검사에 아무 억향 없음)
        conn.execute(
            "INSERT INTO transactions (card_id, type, amount, balance_after, created_at)"
            " VALUES (?, ?, ?, ?, ?)",
            (card_id, type_, amount, max(0, amount * 5 - n * 100), ts),
        )
    # 쟔액을 마지막 거래와 동기화
    conn.execute(
        """
        UPDATE cards SET balance = COALESCE((
            SELECT balance_after FROM transactions
            WHERE card_id = cards.id
            ORDER BY id DESC LIMIT 1
        ), balance)
        """
    )
    conn.commit()
    conn.close()


def grab(widget, name):
    """위젯 전체를 PNG로 저장하고 파일 경로 반환."""
    pix = widget.grab()
    out = SHOTS_DIR / "{}.png".format(name)
    pix.save(str(out), "PNG")
    return str(out.relative_to(ROOT))


def text_overflow_check(widget):
    """위젯 트리를 순회하며 라벨/버튼 텍스트가 엘리스 없이 들어가는지 검사.

    반환: list of dicts {kind, text, w, needed}
    """
    from PyQt5.QtWidgets import QLabel, QPushButton, QLineEdit
    from PyQt5.QtGui import QFontMetrics

    # 진짜 잘림만 보고: 텍스트가 위젯 너비보다 의미 있게 넘치는 경우만
    # (sizeHint에 정확히 맞춰진 라벨은 needed == w 또는 needed - w == 1px라 false positive)
    SLACK = 4  # 픽셀 마진 — 이만큼 넘쳐야 진짜 잘림
    issues = []
    for child in widget.findChildren(QLabel):
        t = child.text()
        if not t or len(t) < 2:
            continue
        if not child.isVisible():
            continue
        if child.wordWrap():
            continue
        fm = QFontMetrics(child.font())
        avail = child.width()
        needed = fm.horizontalAdvance(t)
        if needed > avail + SLACK and avail > 0:
            issues.append({
                "kind": "QLabel",
                "text": t,
                "w": child.width(),
                "needed": needed,
            })
    for child in widget.findChildren(QPushButton):
        t = child.text()
        if not t or len(t) < 2:
            continue
        if not child.isVisible():
            continue
        fm = QFontMetrics(child.font())
        # 버튼은 아이콘 + padding이 있으니 +30 마진
        avail = max(0, child.width() - 30)
        needed = fm.horizontalAdvance(t)
        if needed > avail + SLACK and avail > 0:
            issues.append({
                "kind": "QPushButton",
                "text": t,
                "w": child.width(),
                "needed": needed,
            })
    return issues


def run_screen(name, build_widget, fill_func=None, dialog_modal=False):
    """한 개 화면을 띄움 + 검사 + 스크린샷.

    화면 크기가 USABLE을 초과하면 강제로 USABLE 크기로 resize한 뒤 추가
    스크린샷을 찍는다 — 1366x768 실제 환경에서 ScrollArea/축소 코드가
    제대로 작동하는지 검증한다.
    """
    from PyQt5.QtCore import Qt, QTimer

    w = build_widget()
    try:
        w.setModal(False)
    except Exception:
        pass
    w.setAttribute(Qt.WA_DontShowOnScreen, False)
    w.show()
    from PyQt5.QtWidgets import QApplication
    QApplication.processEvents()
    if fill_func:
        try:
            fill_func(w)
        except Exception as e:
            print("fill error on", name, e)
        QApplication.processEvents()
    QApplication.processEvents()

    natural_w = w.width()
    natural_h = w.height()
    overflow_w = max(0, natural_w - USABLE_W)
    overflow_h = max(0, natural_h - USABLE_H)
    text_issues = text_overflow_check(w)
    shot = grab(w, name)

    # 화면이 작을 때 동작을 시뮬레이션 — fixed size를 풀고 USABLE 크기로 강제 resize
    sim_shot = None
    sim_overflow_h = 0
    if overflow_h > 0:
        try:
            w.setMinimumSize(0, 0)
            w.setMaximumSize(16777215, 16777215)
            w.resize(min(natural_w, USABLE_W), USABLE_H)
            QApplication.processEvents()
            sim_overflow_h = max(0, w.height() - USABLE_H)
            sim_shot = grab(w, name + "_sim768")
        except Exception as e:
            print("sim resize fail", name, e)

    record = {
        "name": name,
        "size": [natural_w, natural_h],
        "fits_width": overflow_w == 0,
        "fits_height": overflow_h == 0,
        "overflow_w": overflow_w,
        "overflow_h": overflow_h,
        "text_clipped_count": len(text_issues),
        "text_clipped": text_issues[:10],
        "screenshot": shot,
        "sim_screenshot": sim_shot,
        "sim_overflow_h": sim_overflow_h,
    }
    REPORT["screens"].append(record)
    print("[{}] natural={}x{}  fits_w={} fits_h={}  text_clipped={}{}".format(
        name, natural_w, natural_h,
        overflow_w == 0, overflow_h == 0, len(text_issues),
        "  sim768={}".format(w.height()) if sim_shot else "",
    ))
    w.close()
    w.deleteLater()
    QApplication.processEvents()


def main():
    seed_db()
    # 쟁이 환경
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("기프트카드 진단")

    from src.ui.theme import apply as apply_theme
    apply_theme(app)

    from src.db import connection as db_conn
    from src.db.schema import init_db
    db_conn.configure(str(TMP_DB))
    init_db()

    notifiers = []  # 팝업 없이 조용히

    # 메인 윈도우
    from src.ui.main_window import MainWindow
    def build_main():
        win = MainWindow(notifiers)
        win.resize(USABLE_W, USABLE_H)
        return win
    run_screen("01_main_window", build_main)

    # 카드 등록 다이얼로그 - 숫자패드 닫힌 상태
    from src.ui.card_register_dialog import CardRegisterDialog
    def build_register_closed():
        dlg = CardRegisterDialog("8800012345", None)
        return dlg
    run_screen("02_register_dialog_closed", build_register_closed)

    # 카드 등록 다이얼로그 - 숫자패드 열린 상태
    def build_register_open():
        dlg = CardRegisterDialog("8800012345", None)
        dlg._kb_btn.setChecked(True)  # 숫자패드 열기
        return dlg
    run_screen("03_register_dialog_open_numpad", build_register_open)

    # 신규 등록 - 기본값 해제 상태 (필드 활성화)
    def build_register_unchecked():
        dlg = CardRegisterDialog("8800012345", None)
        dlg._name_default_cb.setChecked(False)
        dlg._phone_default_cb.setChecked(False)
        dlg._name.setText("이제몔이이해할수없는긴이름")
        dlg._phone.setText("01012345678")
        return dlg
    run_screen("04_register_dialog_long_name", build_register_unchecked)

    # 충전 다이얼로그
    from src.ui.transaction_dialog import TransactionDialog
    def build_charge():
        return TransactionDialog("charge", "8800012345", 50000, None)
    run_screen("05_transaction_charge", build_charge)

    # 결제 다이얼로그 (더 큼)
    def build_pay():
        return TransactionDialog("pay", "8800012345", 50000, None)
    run_screen("06_transaction_pay", build_pay)

    # 결제 다이얼로그 - 금액 입력 후
    def build_pay_filled():
        dlg = TransactionDialog("pay", "8800012345", 1234567, None)
        dlg._amount_input.setText("1,234,567")
        return dlg
    run_screen("07_transaction_pay_large_amount", build_pay_filled)

    # 회원 검색 패널
    from src.ui.member_search import MemberSearchPanel
    def build_member_search():
        p = MemberSearchPanel(None)
        return p
    run_screen("08_member_search", build_member_search)

    # 회원 수정 다이얼로그
    from src.ui.member_edit_dialog import MemberEditDialog
    def build_member_edit():
        dlg = MemberEditDialog(1, "01012345678", "김성수", None)
        return dlg
    run_screen("09_member_edit", build_member_edit)

    # 관리자 패널
    from src.ui.admin_panel import AdminPanel
    def build_admin():
        p = AdminPanel(None)
        return p
    run_screen("10_admin_panel", build_admin)

    # 카드 정보 창 - 첫 번째 카드 사용
    from src.ui.card_info_window import CardInfoWindow
    from src.service import card_service
    # 시드 데이터로 만들어진 첫 카드 바코드 가져오기
    conn = sqlite3.connect(str(TMP_DB))
    conn.row_factory = sqlite3.Row
    first_barcode = conn.execute(
        "SELECT barcode FROM cards ORDER BY id LIMIT 1"
    ).fetchone()["barcode"]
    conn.close()
    info = card_service.lookup(first_barcode)
    def build_card_info():
        return CardInfoWindow(info, notifiers, None)
    run_screen("11_card_info", build_card_info)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(REPORT, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print("\n=== 요약 ===")
    fail_w = [s for s in REPORT["screens"] if not s["fits_width"]]
    fail_h = [s for s in REPORT["screens"] if not s["fits_height"]]
    fail_t = [s for s in REPORT["screens"] if s["text_clipped_count"] > 0]
    print("가로가 넘치는 화면:", [s["name"] for s in fail_w])
    print("세로가 넘치는 화면:", [s["name"] for s in fail_h])
    print("텍스트 잘림 화면:", [s["name"] for s in fail_t])
    print("전체 리포트:", REPORT_PATH)
    # 임시 폴더 정리
    try:
        shutil.rmtree(TMP_DIR, ignore_errors=True)
    except Exception:
        pass


if __name__ == "__main__":
    main()
