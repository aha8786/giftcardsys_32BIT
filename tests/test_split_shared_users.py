"""한 user_id에 카드 N장이 매달려 있는 백업 데이터를 init_db()가 자동 분리하는지 검증."""
import sqlite3

from src.db import connection as db_conn
from src.db.schema import init_db
from src.service import card_service


def _seed_shared(db_path):
    """init_db() 호출 전 raw SQL로 공유 user_id 데이터 주입 (백업 복원 시뮬레이션)."""
    conn = sqlite3.connect(db_path)
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
    # user 1: 카드 3장 / user 2: 카드 2장 / user 3: 카드 1장 (분리 불필요)
    conn.execute("INSERT INTO users(id, phone_number, name) VALUES (1, '01011112222', '홍길동')")
    conn.execute("INSERT INTO users(id, phone_number, name) VALUES (2, '01033334444', '김철수')")
    conn.execute("INSERT INTO users(id, phone_number, name) VALUES (3, '01055556666', '이단독')")
    conn.execute("INSERT INTO cards(id, barcode, user_id, balance) VALUES (1, '11111', 1, 50000)")
    conn.execute("INSERT INTO cards(id, barcode, user_id, balance) VALUES (2, '22222', 1, 50000)")
    conn.execute("INSERT INTO cards(id, barcode, user_id, balance) VALUES (3, '33333', 1, 30000)")
    conn.execute("INSERT INTO cards(id, barcode, user_id, balance) VALUES (4, '44444', 2, 10000)")
    conn.execute("INSERT INTO cards(id, barcode, user_id, balance) VALUES (5, '55555', 2, 20000)")
    conn.execute("INSERT INTO cards(id, barcode, user_id, balance) VALUES (6, '66666', 3, 70000)")
    conn.execute(
        "INSERT INTO transactions(card_id, type, amount, balance_after) VALUES (1, '충전', 50000, 50000)"
    )
    conn.execute(
        "INSERT INTO transactions(card_id, type, amount, balance_after) VALUES (4, '충전', 10000, 10000)"
    )
    conn.commit()
    conn.close()


def test_init_db_splits_shared_users(tmp_path):
    db_file = str(tmp_path / "shared.db")
    _seed_shared(db_file)
    db_conn.configure(db_file)
    init_db()

    conn = sqlite3.connect(db_file)
    user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    card_count = conn.execute("SELECT COUNT(*) FROM cards").fetchone()[0]
    # 공유 user 분리: 6장 카드 모두 별개 user를 가져야 함
    assert user_count == 6
    assert card_count == 6
    # 모든 카드의 user_id는 unique
    distinct_user_ids = conn.execute("SELECT COUNT(DISTINCT user_id) FROM cards").fetchone()[0]
    assert distinct_user_ids == 6
    conn.close()


def test_split_preserves_transactions(tmp_path):
    db_file = str(tmp_path / "shared.db")
    _seed_shared(db_file)
    db_conn.configure(db_file)
    init_db()

    conn = sqlite3.connect(db_file)
    tx_count = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    # 마이그레이션 전 2건 그대로 보존
    assert tx_count == 2
    conn.close()


def test_after_split_name_change_is_independent(tmp_path):
    db_file = str(tmp_path / "shared.db")
    _seed_shared(db_file)
    db_conn.configure(db_file)
    init_db()

    rows = card_service.search_users("")
    target = next(r for r in rows if r["barcode"] == "22222")
    card_service.update_user(target["id"], target["phone_number"], "이몽룡")

    after = {r["barcode"]: r["name"] for r in card_service.search_users("")}
    # 22222만 이몽룡, 같은 phone을 쓰던 11111/33333은 홍길동 그대로
    assert after["22222"] == "이몽룡"
    assert after["11111"] == "홍길동"
    assert after["33333"] == "홍길동"
    # 김철수/이단독도 영향 없음
    assert after["44444"] == "김철수"
    assert after["55555"] == "김철수"
    assert after["66666"] == "이단독"


def test_init_db_is_idempotent(tmp_path):
    """init_db()를 두 번 호출해도 분리가 더 일어나거나 깨지지 않아야 한다."""
    db_file = str(tmp_path / "shared.db")
    _seed_shared(db_file)
    db_conn.configure(db_file)
    init_db()
    init_db()  # 두 번째 호출

    conn = sqlite3.connect(db_file)
    user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    card_count = conn.execute("SELECT COUNT(*) FROM cards").fetchone()[0]
    assert user_count == 6  # 첫 호출에서 분리된 후 더 늘어나면 안 됨
    assert card_count == 6
    conn.close()


def test_deleted_placeholder_not_split(tmp_path):
    """탈퇴 회원용 placeholder('__deleted__')는 의도적인 공유라 분리 대상이 아니다."""
    db_file = str(tmp_path / "deleted.db")
    db_conn.configure(db_file)
    init_db()  # 빈 DB 초기화

    # placeholder 회원 + 카드 두 장을 그 회원에 매달기
    conn = sqlite3.connect(db_file)
    conn.execute("INSERT INTO users(id, phone_number, name) VALUES (100, '__deleted__', '(삭제)')")
    conn.execute("INSERT INTO cards(id, barcode, user_id, balance) VALUES (10, 'd1', 100, 0)")
    conn.execute("INSERT INTO cards(id, barcode, user_id, balance) VALUES (11, 'd2', 100, 0)")
    conn.commit()
    conn.close()

    init_db()  # 마이그레이션 다시 실행

    conn = sqlite3.connect(db_file)
    placeholder_user_count = conn.execute(
        "SELECT COUNT(*) FROM users WHERE phone_number = '__deleted__'"
    ).fetchone()[0]
    assert placeholder_user_count == 1  # 분리되지 않고 단일 placeholder 유지
    conn.close()
