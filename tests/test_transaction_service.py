import pytest
from src.service import card_service, transaction_service as svc
from src.db import connection as db_conn
from src.db import queries as q
from src.exceptions import InsufficientBalanceError, InvalidAmountError, CardNotFoundError


def _register(barcode="1000000001", phone="010-0000-0001", balance=10000):
    card_service.register(barcode, phone, balance)
    return barcode


def test_charge_increases_balance(db):
    barcode = _register()
    result = svc.charge(barcode, 5000)
    assert result["balance"] == 15000

    info = card_service.lookup(barcode)
    assert info["card"]["balance"] == 15000


def test_pay_decreases_balance(db):
    barcode = _register()
    result = svc.pay(barcode, 3000)
    assert result["balance"] == 7000

    info = card_service.lookup(barcode)
    assert info["card"]["balance"] == 7000


def test_pay_exact_balance(db):
    barcode = _register()
    result = svc.pay(barcode, 10000)
    assert result["balance"] == 0


def test_pay_insufficient_balance_raises(db):
    barcode = _register(balance=5000)
    with pytest.raises(InsufficientBalanceError):
        svc.pay(barcode, 6000)


def test_balance_unchanged_after_failed_pay(db):
    barcode = _register(balance=5000)
    with pytest.raises(InsufficientBalanceError):
        svc.pay(barcode, 9999)
    info = card_service.lookup(barcode)
    assert info["card"]["balance"] == 5000


def test_balance_after_invariant(db):
    """cards.balance must equal the latest transaction's balance_after."""
    barcode = _register(balance=10000)
    svc.charge(barcode, 2000)
    svc.pay(barcode, 4000)

    with db_conn.get_db() as conn:
        card = q.find_card_by_barcode(conn, barcode)
        txs = q.fetch_transactions_by_card(conn, card["id"])
        assert card["balance"] == txs[0]["balance_after"]


def test_invalid_amount_raises(db):
    barcode = _register()
    with pytest.raises(InvalidAmountError):
        svc.charge(barcode, 0)
    with pytest.raises(InvalidAmountError):
        svc.charge(barcode, -100)
    with pytest.raises(InvalidAmountError):
        svc.charge(barcode, "abc")


def test_card_not_found_raises(db):
    with pytest.raises(CardNotFoundError):
        svc.charge("9999999999", 1000)
