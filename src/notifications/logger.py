import logging
from datetime import datetime

from src.notifications.base import Notifier

_logger = logging.getLogger("giftcard")


def configure_logger(log_path: str) -> None:
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    _logger.addHandler(handler)
    _logger.setLevel(logging.INFO)


class LogNotifier(Notifier):
    def notify(self, event: str, context: dict) -> None:
        _logger.info("event=%s context=%s", event, context)
