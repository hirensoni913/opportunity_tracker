import os
from celery import shared_task

from notification.helpers.base import NotificationService
from notification.helpers.email_helper import EmailNotificationChannel
from notification.helpers.whatsapp_helper import WhatsAppNotificationChannel
from notification.helpers.sms_helper import SMSNotificationChannel
from .models import NotificationChannel, NotificationSubscription, OpportunitySubscription
from tracker.models import Opportunity
from django.core.mail import send_mail


@shared_task
def send_new_opportunity_notifications(opportunity_id):
    try:
        opportunity = Opportunity.objects.get(id=opportunity_id)

        # Fetch "New Opportunity" Notification channel
        channel = NotificationChannel.objects.get(
            name=os.environ.get("NEW_OPPORTUNITY_ALERT_CHANNEL"))

        # Get all the active subscriptions
        subscriptions = NotificationSubscription.objects.filter(
            channel=channel, is_active=True)

        email_message = f"An opportunity [{
            opportunity.title}] been created. Please check the portal for more details."
        short_message = f"An opportunity [{
            opportunity.title}] has been created."
        execute_channel_send(subscriptions, subject="New Opportunity Created",
                             email_message=email_message, short_message=short_message)

    except (Opportunity.DoesNotExist, NotificationChannel.DoesNotExist) as e:
        print(f"Error [DoesNotExist]: {e}")
    except Exception as e:
        print(f"An unhandled exception occurred: {e}")


@shared_task
def send_opportunity_update_emails(opportunity_id):
    try:
        opportunity = Opportunity.objects.get(id=opportunity_id)
        subscriptions = OpportunitySubscription.objects.filter(
            opportunity=opportunity, is_active=True)

        email_message = f"An opportunity you are subscribed [{
            opportunity.title}] to has been updated. Please check the portal for more details."
        short_message = f"An opportunity you are subscribed [{
            opportunity.title}] to has been updated."
        execute_channel_send(subscriptions, subject="Opportunity Update",
                             email_message=email_message, short_message=short_message)

    except (Opportunity.DoesNotExist) as e:
        print("Error [DoesNotExists]:", e)
    except Exception as e:
        print("An unhandled exception occurred:", e)


def execute_channel_send(subscriptions, subject="", email_message="", short_message=""):
    # Map each channel with the preferred method
    channels_map = {
        'email': EmailNotificationChannel(),
        'whatsapp': WhatsAppNotificationChannel(),
        'sms': SMSNotificationChannel(),
    }

    # Group notifications by channel
    notification_by_channel = {}

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
