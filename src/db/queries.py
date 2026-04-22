import sqlite3
from typing import Optional


# ── users ──────────────────────────────────────────────────────────────────

def insert_user(conn: sqlite3.Connection, phone_number: str) -> int:
    cur = conn.execute(
        "INSERT INTO users (phone_number) VALUES (?)",
        (phone_number,),
    )
    return cur.lastrowid


def find_user_by_phone(conn: sqlite3.Connection, phone_number: str) -> Optional[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM users WHERE phone_number = ?",
        (phone_number,),
    ).fetchone()


def fetch_all_users(conn: sqlite3.Connection) -> list:
    return conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()


def update_user_phone(conn: sqlite3.Connection, user_id: int, phone_number: str) -> None:
    conn.execute(
        "UPDATE users SET phone_number = ? WHERE id = ?",
        (phone_number, user_id),
    )


def search_users(conn: sqlite3.Connection, keyword: str) -> list:
    like = f"%{keyword}%"
    return conn.execute(
        """
        SELECT u.*, c.barcode, c.balance
        FROM users u
        LEFT JOIN cards c ON c.user_id = u.id
        WHERE u.phone_number LIKE ? OR c.barcode LIKE ?
        ORDER BY u.created_at DESC, c.created_at DESC
        """,
        (like, like),
    ).fetchall()


# ── cards ──────────────────────────────────────────────────────────────────

def insert_card(conn: sqlite3.Connection, barcode: str, user_id: int, balance: int) -> int:
    cur = conn.execute(
        "INSERT INTO cards (barcode, user_id, balance) VALUES (?, ?, ?)",
        (barcode, user_id, balance),
    )
    return cur.lastrowid


def find_card_by_barcode(conn: sqlite3.Connection, barcode: str) -> Optional[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM cards WHERE barcode = ?",
        (barcode,),
    ).fetchone()


def find_cards_by_user_id(conn: sqlite3.Connection, user_id: int) -> list:
    return conn.execute(
        "SELECT * FROM cards WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    ).fetchall()


def update_card_balance(conn: sqlite3.Connection, card_id: int, new_balance: int) -> None:
    conn.execute(
        "UPDATE cards SET balance = ? WHERE id = ?",
        (new_balance, card_id),
    )


def fetch_total_balance(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT COALESCE(SUM(balance), 0) AS total FROM cards").fetchone()
    return row["total"]


# ── transactions ────────────────────────────────────────────────────────────

def insert_transaction(
    conn: sqlite3.Connection,
    card_id: int,
    tx_type: str,
    amount: int,
    balance_after: int,
) -> int:
    cur = conn.execute(
        "INSERT INTO transactions (card_id, type, amount, balance_after) VALUES (?, ?, ?, ?)",
        (card_id, tx_type, amount, balance_after),
    )
    return cur.lastrowid


def fetch_transactions_by_card(conn: sqlite3.Connection, card_id: int) -> list:
    return conn.execute(
        "SELECT * FROM transactions WHERE card_id = ? ORDER BY created_at DESC, id DESC",
        (card_id,),
    ).fetchall()


def fetch_transactions_by_period(
    conn: sqlite3.Connection, start: str, end: str
) -> list:
    return conn.execute(
        "SELECT * FROM transactions WHERE created_at BETWEEN ? AND ? ORDER BY created_at DESC, id DESC",
        (start, end),
    ).fetchall()


def fetch_transactions_filtered(
    conn: sqlite3.Connection,
    start: str,
    end: str,
    barcode: str = "",
    phone: str = "",
) -> list:
    """Return transactions joined with card barcode and user phone, with optional filters."""
    conditions = ["t.created_at BETWEEN :start AND :end"]
    params: dict = {"start": start, "end": end}
    if barcode:
        conditions.append("c.barcode LIKE :barcode")
        params["barcode"] = f"%{barcode}%"
    if phone:
        conditions.append("u.phone_number LIKE :phone")
        params["phone"] = f"%{phone}%"

    where = " AND ".join(conditions)
    sql = f"""
        SELECT t.id, t.card_id, c.barcode, u.phone_number,
               t.type, t.amount, t.balance_after, t.created_at
        FROM transactions t
        JOIN cards c ON c.id = t.card_id
        JOIN users u ON u.id = c.user_id
        WHERE {where}
        ORDER BY t.created_at DESC, t.id DESC
    """
    return conn.execute(sql, params).fetchall()


def fetch_stats_by_period(conn: sqlite3.Connection, start: str, end: str) -> sqlite3.Row:
    return conn.execute(
        """
        SELECT
            COALESCE(SUM(CASE WHEN type = '충전' THEN amount ELSE 0 END), 0) AS total_charged,
            COALESCE(SUM(CASE WHEN type = '사용' THEN amount ELSE 0 END), 0) AS total_used
        FROM transactions
        WHERE created_at BETWEEN ? AND ?
        """,
        (start, end),
    ).fetchone()
