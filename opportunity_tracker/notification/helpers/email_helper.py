from django.core.mail import EmailMultiAlternatives, send_mail
from django.utils.html import strip_tags
from .base import NotificationChannel


class EmailNotificationChannel(NotificationChannel):
    def send(self, recipients, **kwargs):
        subject = kwargs.get("subject")
        message = kwargs.get("message")

        if not subject or not message:
            raise ValueError(
                "Email notification requires both subject and message")

        if recipients:
            plain_text = strip_tags(message)
            email = send_mail(
                subject=subject,
                message=plain_text,
                from_email="noreply@swisstph.ch",
                recipient_list=recipients,
                html_message=message,
            )
            return email
