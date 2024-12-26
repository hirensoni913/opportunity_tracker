from abc import ABC, abstractmethod


class NotificationChannel(ABC):

    @abstractmethod
    def send(self, recipients, **kwargs):
        pass


class NotificationService:
    def __init__(self, channels=None) -> None:
        self.channels = channels or []

    def notify(self, recipients, **kwargs):
        for channel in self.channels:
            channel.send(recipients, **kwargs)
