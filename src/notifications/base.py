from abc import ABC, abstractmethod


class Notifier(ABC):
    @abstractmethod
    def notify(self, event: str, context: dict) -> None:
        """Send a notification for the given event."""
