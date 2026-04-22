import logging

import requests

from config import settings
from src.notifications.base import Notifier

_logger = logging.getLogger("giftcard.kakao")

_TEMPLATE_MAP = {
    "card_registered": settings.KAKAO_TEMPLATE_CODE_REGISTER,
    "charged": settings.KAKAO_TEMPLATE_CODE_CHARGE,
    "paid": settings.KAKAO_TEMPLATE_CODE_PAYMENT,
}

_MESSAGES = {
    "card_registered": "[기프트카드 등록] 바코드 {barcode} / 잔액 {balance:,}원",
    "charged": "[충전 완료] 충전 금액 {amount:,}원 / 현재 잔액 {balance:,}원",
    "paid": "[결제 완료] 결제 금액 {amount:,}원 / 잔액 {balance:,}원",
}


def _is_configured() -> bool:
    return bool(settings.KAKAO_API_KEY and settings.KAKAO_SENDER_KEY)


class KakaoNotifier(Notifier):
    def notify(self, event: str, context: dict) -> None:
        if not _is_configured():
            _logger.debug("카카오 API 키 미설정 — 알림 건너뜀 (event=%s)", event)
            return

        phone = context.get("phone_number", "")
        if not phone:
            return

        template_code = _TEMPLATE_MAP.get(event, "")
        msg_template = _MESSAGES.get(event, "")
        if not template_code or not msg_template:
            return

        try:
            message = msg_template.format(**context)
            payload = {
                "apikey": settings.KAKAO_API_KEY,
                "userid": settings.KAKAO_SENDER_KEY,
                "senderkey": settings.KAKAO_SENDER_KEY,
                "tpl_code": template_code,
                "sender": phone,
                "receiver_1": phone,
                "recvname_1": "",
                "subject_1": "기프트카드 알림",
                "message_1": message,
                "failover": "N",
            }
            resp = requests.post(settings.KAKAO_API_URL, data=payload, timeout=5)
            resp.raise_for_status()
            _logger.info("카카오 알림 전송 성공 (event=%s, phone=%s)", event, phone)
        except Exception as exc:
            _logger.warning("카카오 알림 전송 실패 (event=%s): %s", event, exc)
