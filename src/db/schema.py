import sqlite3

from src.db.connection import get_db

_CREATE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number TEXT    NOT NULL,
    name         TEXT    NOT NULL DEFAULT '홍길동',
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

_CREATE_CARDS = """
CREATE TABLE IF NOT EXISTS cards (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode    TEXT    UNIQUE NOT NULL,
    user_id    INTEGER NOT NULL REFERENCES users(id),
    balance    INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

_CREATE_TRANSACTIONS = """
CREATE TABLE IF NOT EXISTS transactions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id      INTEGER NOT NULL REFERENCES cards(id),
    type         TEXT    NOT NULL CHECK(type IN ('충전', '사용')),
    amount       INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

_CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_cards_barcode    ON cards(barcode)",
    "CREATE INDEX IF NOT EXISTS idx_cards_user_id    ON cards(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_tx_card_id       ON transactions(card_id)",
    "CREATE INDEX IF NOT EXISTS idx_tx_created_at    ON transactions(created_at)",
]


_DELETED_PLACEHOLDER_PHONE = "__deleted__"


def _split_shared_users(conn: sqlite3.Connection) -> int:
    """한 user_id에 카드 N장(N>1)이 매달려 있으면 N-1개 카드를 새 user로 분리.

    배경: 정책 변경 [2026-05-01] 이전 데이터(또는 그 시점 백업의 복원본)에서는
    같은 phone_number는 같은 user_id를 공유했음. 이 상태 그대로 두면 회원
    정보 수정 시 한 카드의 이름을 바꾸면 같은 user에 매달린 다른 카드의
    이름까지 함께 바뀐다(공유 회원 row 한 개를 update하므로).

    이 함수는 그런 공유 user를 발견하면 카드 단위로 별개의 user row로 분리한다.
    transactions는 card_id 외래키만 가지고 있으므로 거래내역에는 영향 없음.

    삭제된 회원용 placeholder('__deleted__')는 의도된 공유라 건드리지 않음.

    반환값: 새로 만든 user row 개수 (0이면 분리할 게 없었다는 뜻).
    """
    rows = conn.execute(
        """
        SELECT c.id AS card_id, c.user_id, u.phone_number, u.name, u.created_at
        FROM cards c
        JOIN users u ON u.id = c.user_id
        WHERE c.user_id IN (
            SELECT user_id FROM cards
            GROUP BY user_id
            HAVING COUNT(*) > 1
        )
        AND u.phone_number != ?
        ORDER BY c.user_id, c.id
        """,
        (_DELETED_PLACEHOLDER_PHONE,),
    ).fetchall()

    new_user_count = 0
    seen_users = set()
    for row in rows:
        card_id, user_id, phone, name, created_at = row
        # 각 user_id에 매달린 카드 중 첫 번째 카드는 기존 user에 그대로 두고,
        # 두 번째부터는 새 user를 만들어 분리한다.
        if user_id not in seen_users:
            seen_users.add(user_id)
            continue
        cur = conn.execute(
            "INSERT INTO users (phone_number, name, created_at) VALUES (?, ?, ?)",
            (phone, name, created_at),
        )
        new_user_id = cur.lastrowid
        conn.execute(
            "UPDATE cards SET user_id = ? WHERE id = ?",
            (new_user_id, card_id),
        )
        new_user_count += 1
    return new_user_count


def init_db() -> None:
    with get_db() as conn:
        conn.execute(_CREATE_USERS)
        conn.execute(_CREATE_CARDS)
        conn.execute(_CREATE_TRANSACTIONS)
        for idx_sql in _CREATE_INDEXES:
            conn.execute(idx_sql)
        cur = conn.execute("PRAGMA table_info(users)")
        cols = [r[1] for r in cur.fetchall()]
        if "name" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN name TEXT NOT NULL DEFAULT '홍길동'")
        # 백업 복원 등으로 들어온 공유 user 카드를 자동 분리
        _split_shared_users(conn)
