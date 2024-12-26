from .base import NotificationChannel


class SMSNotificationChannel(NotificationChannel):
    def send(self, recipients, **kwargs):
        message = kwargs.get('message')
        if not message:
            raise ValueError("SMS requires a message")

        for recipient in recipients:
            # Call SMS API
            print(f"Sending SMS to {recipient}")
