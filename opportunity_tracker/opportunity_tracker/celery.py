from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module for the 'Celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opportunity_tracker.settings')

app = Celery('opportunity_tracker')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover task in all applications
app.autodiscover_tasks()


def debug_task(self):
    print(f"Request: {self.request!r}")
