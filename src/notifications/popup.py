from PyQt5.QtWidgets import QMessageBox

from src.notifications.base import Notifier

_EVENT_MESSAGES = {
    "card_registered": "카드가 등록되었습니다.",
    "charged": "충전이 완료되었습니다.",
    "paid": "결제가 완료되었습니다.",
    "low_balance": "잔액이 부족합니다.",
}


class PopupNotifier(Notifier):
    def notify(self, event: str, context: dict) -> None:
        title = "기프트카드 알림"
        base_msg = _EVENT_MESSAGES.get(event, event)

        if event == "card_registered":
            msg = f"{base_msg}\n바코드: {context.get('barcode', '')}\n잔액: {context.get('balance', 0):,}원"
        elif event in ("charged", "paid"):
            msg = f"{base_msg}\n금액: {context.get('amount', 0):,}원\n잔액: {context.get('balance', 0):,}원"
        elif event == "low_balance":
            msg = f"{base_msg}\n현재 잔액: {context.get('balance', 0):,}원"
        else:
            msg = base_msg

        QMessageBox.information(None, title, msg)
