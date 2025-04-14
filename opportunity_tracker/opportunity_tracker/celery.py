from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'Celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opportunity_tracker.settings')

app = Celery('opportunity_tracker')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover task in all applications
app.autodiscover_tasks()
app.conf.enable_utc = False
app.conf.timezone = settings.TIME_ZONE
app.conf.beat_schedule_filename = os.getenv(
    "CELERY_BEAT_SCHEDULE_FILENAME", "celerybeat-schedule")


def debug_task(self):
    print(f"Request: {self.request!r}")
