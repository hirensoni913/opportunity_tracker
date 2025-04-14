from urllib.parse import urljoin
from celery import shared_task
import datetime

from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse

from notification.models import NotificationSubscription
from notification.tasks import execute_channel_send

from .models import Opportunity


@shared_task
def send_weekly_summary(channel: str, days: int = 7):
    print(
        f"📬 Sending a weekly summary for the channel {channel} at {datetime.datetime.now()}")
    date_from = datetime.datetime.now() - datetime.timedelta(days=days)
    opportunities = Opportunity.objects.filter(
        created_at__gte=date_from).order_by('-created_at')

    if not opportunities.exists():
        return "No new opportunities to send."

    # Get all the active subscriptions
    subscriptions = NotificationSubscription.objects.filter(
        channel__name=channel, is_active=True)
    subscription_ids = list(subscriptions.values_list('id', flat=True))

    context = {
        'opportunities': opportunities,
        'date_from': date_from,
        'date_to': datetime.datetime.now(),
        'site_url': settings.SITE_URL,
    }
    email_message = render_to_string(
        'tracker/emails/weekly_summary.html', context)

    short_message = f"{opportunities.count()} new opportunities created this week."

    execute_channel_send.delay(subscription_ids, NotificationSubscription.__name__, subject="Your Weekly Summary",
                               email_message=email_message, short_message=short_message)

    return f"Weekly summary sent to {len(subscription_ids)} subscribers for channel '{channel}'."
