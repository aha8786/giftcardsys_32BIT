from src.db import connection as db
from src.db import queries as q
from src.exceptions import (
    CardNotFoundError,
    InsufficientBalanceError,
    InvalidAmountError,
)


def _validate_amount(amount) -> int:
    try:
        amount = int(amount)
    except (TypeError, ValueError):
        raise InvalidAmountError(amount)
    if amount <= 0:
        raise InvalidAmountError(amount)
    return amount


def charge(barcode: str, amount) -> dict:
    amount = _validate_amount(amount)
    with db.get_db() as conn:
        card = q.find_card_by_barcode(conn, barcode)
        if not card:
            raise CardNotFoundError(barcode)

        new_balance = card["balance"] + amount
        q.update_card_balance(conn, card["id"], new_balance)
        tx_id = q.insert_transaction(conn, card["id"], "충전", amount, new_balance)

    return {"tx_id": tx_id, "balance": new_balance, "amount": amount}


def pay(barcode: str, amount) -> dict:
    amount = _validate_amount(amount)
    with db.get_db() as conn:
        card = q.find_card_by_barcode(conn, barcode)
        if not card:
            raise CardNotFoundError(barcode)

        new_balance = card["balance"] - amount
        if new_balance < 0:
            raise InsufficientBalanceError(card["balance"], amount)

        q.update_card_balance(conn, card["id"], new_balance)
        tx_id = q.insert_transaction(conn, card["id"], "사용", amount, new_balance)

    return {"tx_id": tx_id, "balance": new_balance, "amount": amount}
