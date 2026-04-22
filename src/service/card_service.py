import sqlite3

from src.db import connection as db
from src.db import queries as q
from src.exceptions import (
    CardNotFoundError,
    DuplicateBarcodeError,
    InvalidAmountError,
    InvalidBarcodeError,
)


def _validate_barcode(barcode: str) -> str:
    barcode = barcode.strip()
    if not barcode or not barcode.isdigit():
        raise InvalidBarcodeError(barcode)
    return barcode


def lookup(barcode: str) -> dict:
    barcode = _validate_barcode(barcode)
    with db.get_db() as conn:
        card = q.find_card_by_barcode(conn, barcode)
        if not card:
            raise CardNotFoundError(barcode)
        user = conn.execute("SELECT * FROM users WHERE id = ?", (card["user_id"],)).fetchone()
        txs = q.fetch_transactions_by_card(conn, card["id"])
        return {
            "card": dict(card),
            "user": dict(user),
            "transactions": [dict(t) for t in txs],
        }


def register(barcode: str, phone_number: str, initial_amount: int) -> dict:
    barcode = _validate_barcode(barcode)
    phone_number = phone_number.strip()
    if not phone_number:
        raise ValueError("전화번호를 입력해 주세요.")
    if initial_amount < 0:
        raise InvalidAmountError(initial_amount)

    with db.get_db() as conn:
        if q.find_card_by_barcode(conn, barcode):
            raise DuplicateBarcodeError(barcode)

        user = q.find_user_by_phone(conn, phone_number)
        user_id = user["id"] if user else q.insert_user(conn, phone_number)

        card_id = q.insert_card(conn, barcode, user_id, initial_amount)
        if initial_amount > 0:
            q.insert_transaction(conn, card_id, "충전", initial_amount, initial_amount)

        return {"card_id": card_id, "user_id": user_id, "balance": initial_amount}


def update_user_phone(user_id: int, phone_number: str) -> None:
    phone_number = phone_number.strip()
    if not phone_number:
        raise ValueError("전화번호를 입력해 주세요.")
    with db.get_db() as conn:
        q.update_user_phone(conn, user_id, phone_number)


def search_users(keyword: str) -> list:
    with db.get_db() as conn:
        rows = q.search_users(conn, keyword.strip())
        return [dict(r) for r in rows]


def get_transactions_filtered(start: str, end: str, barcode: str = "", phone: str = "") -> list:
    s = f"{start} 00:00:00"
    e = f"{end} 23:59:59"
    with db.get_db() as conn:
        rows = q.fetch_transactions_filtered(conn, s, e, barcode, phone)
        return [dict(r) for r in rows]


def find_cards_by_phone(phone_number: str) -> list:
    phone_number = phone_number.strip()
    with db.get_db() as conn:
        user = q.find_user_by_phone(conn, phone_number)
        if not user:
            return []
        cards = q.find_cards_by_user_id(conn, user["id"])
        result = []
        for card in cards:
            txs = q.fetch_transactions_by_card(conn, card["id"])
            result.append({
                "card": dict(card),
                "transactions": [dict(t) for t in txs],
            })
        return result
