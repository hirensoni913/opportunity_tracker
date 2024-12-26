from django.core.mail import send_mail
from .base import NotificationChannel


class EmailNotificationChannel(NotificationChannel):
    def send(self, recipients, **kwargs):
        subject = kwargs.get("subject")
        message = kwargs.get("message")

        if not subject or not message:
            raise ValueError(
                "Email notification requires both subject and message")
        if recipients:
            send_mail(
                subject=subject,
                message=message,
                from_email="noreply@swisstph.ch",
                recipient_list=recipients
            )
