import pytest
from src.service import card_service as svc
from src.exceptions import CardNotFoundError, DuplicateBarcodeError, InvalidBarcodeError


def test_register_and_lookup(db):
    result = svc.register("1234567890", "010-1234-5678", 10000)
    assert result["balance"] == 10000

    info = svc.lookup("1234567890")
    assert info["card"]["balance"] == 10000
    assert info["user"]["phone_number"] == "010-1234-5678"
    assert len(info["transactions"]) == 1
    assert info["transactions"][0]["type"] == "충전"


def test_register_duplicate_barcode_raises(db):
    svc.register("9999", "010-0000-0000", 5000)
    with pytest.raises(DuplicateBarcodeError):
        svc.register("9999", "010-1111-1111", 3000)


def test_lookup_unknown_barcode_raises(db):
    with pytest.raises(CardNotFoundError):
        svc.lookup("0000000000")


def test_invalid_barcode_raises(db):
    with pytest.raises(InvalidBarcodeError):
        svc.lookup("abc")
    with pytest.raises(InvalidBarcodeError):
        svc.lookup("")


def test_register_zero_initial_amount_no_transaction(db):
    svc.register("5555", "010-2222-3333", 0)
    info = svc.lookup("5555")
    assert info["card"]["balance"] == 0
    assert len(info["transactions"]) == 0


def test_same_phone_reuses_user(db):
    r1 = svc.register("1111", "010-9999-9999", 1000)
    r2 = svc.register("2222", "010-9999-9999", 2000)
    assert r1["user_id"] == r2["user_id"]


def test_find_cards_by_phone(db):
    svc.register("3333", "010-7777-8888", 5000)
    svc.register("4444", "010-7777-8888", 3000)
    cards = svc.find_cards_by_phone("010-7777-8888")
    assert len(cards) == 2
