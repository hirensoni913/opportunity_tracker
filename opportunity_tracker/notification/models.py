from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class NotificationChannel(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    default_method = models.CharField(max_length=15, choices=[(
        'email', 'Email'), ('whatsapp', "WhatsApp"), ('sms', 'SMS')], default='email')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        db_table = 'notification_channels'

    def __str__(self):
        return self.name


class NotificationSubscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    channel = models.ForeignKey(NotificationChannel, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    preferred_method = models.CharField(max_length=15, choices=[(
        'email', 'Email'), ('whatsapp', "WhatsApp"), ('sms', 'SMS')], default='email')

    class Meta:
        db_table = 'notification_subscriptions'

    def __str__(self):
        return f"{self.user.username} - {self.channel.name}"


class OpportunitySubscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    opportunity = models.ForeignKey(
        'tracker.Opportunity', on_delete=models.CASCADE)
    preferred_method = models.CharField(max_length=15, choices=[(
        'email', 'Email'), ('whatsapp', "WhatsApp"), ('sms', 'SMS')], default='email')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'opportunity_subscriptions'
        ordering = ['user__first_name',
                    'user__last_name', 'opportunity__ref_no']
