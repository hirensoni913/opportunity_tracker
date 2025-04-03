import os
from celery import shared_task
from django.apps import apps
from django.urls import reverse
from requests import request

from notification.helpers.base import NotificationService
from notification.helpers.email_helper import EmailNotificationChannel
from notification.helpers.whatsapp_helper import WhatsAppNotificationChannel
from notification.helpers.sms_helper import SMSNotificationChannel
from .models import NotificationChannel, NotificationSubscription, OpportunitySubscription
from tracker.models import Opportunity
from django.core.mail import send_mail
from django.template.loader import render_to_string


@shared_task
def execute_channel_send(subscription_ids, model, subject="", email_message="", short_message=""):
    # Map each channel with the preferred method
    channels_map = {
        'email': EmailNotificationChannel(),
        'whatsapp': WhatsAppNotificationChannel(),
        'sms': SMSNotificationChannel(),
    }

    # Group notifications by channel
    notification_by_channel = {}

    ModelClass = apps.get_model('notification', model)
    subscriptions = ModelClass.objects.filter(
        id__in=subscription_ids)

    for subscription in subscriptions:
        preferred_method = subscription.preferred_method
        if preferred_method in channels_map:
            channel = channels_map[preferred_method]
            if channel not in notification_by_channel:
                notification_by_channel[channel] = []
            notification_by_channel[channel].append(
                subscription.user.email if preferred_method == 'email' else subscription.user.phone_number)

    # Send notification via each channel
    for channel, recipients in notification_by_channel.items():
        if isinstance(channel, EmailNotificationChannel):
            channel.send(
                recipients=recipients,
                subject=subject,
                message=email_message
            )
        else:
            channel.send(
                recipients=recipients,
                message=short_message
            )
