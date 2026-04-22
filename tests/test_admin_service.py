from datetime import date
from src.service import card_service, transaction_service, admin_service as svc


def _today() -> str:
    return date.today().isoformat()


def test_stats_empty(db):
    result = svc.get_stats(_today(), _today())
    assert result["total_charged"] == 0
    assert result["total_used"] == 0
    assert result["total_balance"] == 0


def test_stats_after_transactions(db):
    card_service.register("8888", "010-8888-8888", 0)
    transaction_service.charge("8888", 20000)
    transaction_service.pay("8888", 5000)

    result = svc.get_stats(_today(), _today())
    assert result["total_charged"] == 20000
    assert result["total_used"] == 5000
    assert result["total_balance"] == 15000


def test_stats_total_balance_across_cards(db):
    card_service.register("1001", "010-1001-1001", 10000)
    card_service.register("1002", "010-1002-1002", 20000)

    result = svc.get_stats(_today(), _today())
    assert result["total_balance"] == 30000


def test_stats_period_filter(db):
    card_service.register("7777", "010-7777-7777", 0)
    transaction_service.charge("7777", 10000)

    result_today = svc.get_stats(_today(), _today())
    result_past = svc.get_stats("2000-01-01", "2000-01-02")

    assert result_today["total_charged"] == 10000
    assert result_past["total_charged"] == 0
