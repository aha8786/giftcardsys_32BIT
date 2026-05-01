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
