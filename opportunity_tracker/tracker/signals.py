from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Opportunity
from notification.tasks import send_new_opportunity_notifications, send_opportunity_update_emails


@receiver(post_save, sender=Opportunity)
def notify_new_opportunity(sender, instance, created, **kwargs):
    if created:
        # Trigger Celery task to send notification asynchronously
        send_new_opportunity_notifications(instance.id)
    else:
        send_opportunity_update_emails(instance.id)
