import os
from urllib.parse import urljoin
from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from notification.models import NotificationChannel, NotificationSubscription, OpportunitySubscription
from .models import Opportunity
from notification.tasks import execute_channel_send


@receiver(post_save, sender=Opportunity)
def notify_new_opportunity(sender, instance, created, **kwargs):
    try:
        if created:
            # Trigger Celery task to send notification asynchronously
            _send_new_opportunity_notification(instance)
        else:
            # send_opportunity_update_emails(instance.id)
            _send_opportunity_update_notification(instance)
    except (Opportunity.DoesNotExist) as e:
        print("Error [DoesNotExists]:", e)
    except Exception as e:
        print("An unhandled exception occurred:", e)


def _send_new_opportunity_notification(opportunity):
    opportunity = Opportunity.objects.get(id=opportunity.id)

    # Fetch "New Opportunity" Notification channel
    channel = NotificationChannel.objects.get(
        name=os.environ.get("NEW_OPPORTUNITY_ALERT_CHANNEL"))

    # Get all the active subscriptions
    subscriptions = NotificationSubscription.objects.filter(
        channel=channel, is_active=True)
    subscription_ids = list(subscriptions.values_list('id', flat=True))

    relative_url = reverse('opportunity_anonymous', kwargs={
        'pk': opportunity.pk})
    opportunity_url = urljoin(settings.SITE_URL, relative_url)

    context = {
        'opportunity': opportunity,
        'opportunity_url': opportunity_url,
    }
    email_message = render_to_string(
        'tracker/emails/opportunity_created.txt', context)

    short_message = f"An opportunity [{
        opportunity.title}] has been created."

    execute_channel_send.delay(subscription_ids, NotificationSubscription.__name__, subject="New Opportunity Found",
                               email_message=email_message, short_message=short_message)


def _send_opportunity_update_notification(opportunity):
    opportunity = Opportunity.objects.get(id=opportunity.id)
    subscriptions = OpportunitySubscription.objects.filter(
        opportunity=opportunity, is_active=True)
    subscription_ids = list(subscriptions.values_list('id', flat=True))

    relative_url = reverse('opportunity_anonymous', kwargs={
        'pk': opportunity.pk})
    opportunity_url = urljoin(settings.SITE_URL, relative_url)

    context = {
        'opportunity': opportunity,
        'opportunity_url': opportunity_url,
    }
    email_message = render_to_string(
        'tracker/emails/opportunity_update.txt', context)

    short_message = f"An opportunity you are subscribed [{
        opportunity.title}] to has been updated."

    execute_channel_send.delay(subscription_ids, OpportunitySubscription.__name__, subject="Opportunity Update",
                               email_message=email_message, short_message=short_message)
