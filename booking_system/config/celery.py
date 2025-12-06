"""
Celery configuration for booking system.
"""
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('booking_system')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Periodic task schedule
from celery.schedules import crontab

app.conf.beat_schedule = {
    'send-appointment-reminders': {
        'task': 'notifications.tasks.send_appointment_reminders',
        'schedule': crontab(minute=0),  # Every hour at minute 0
    },
    'send-follow-up-notifications': {
        'task': 'notifications.tasks.send_follow_up_notifications',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
    },
    'retry-failed-notifications': {
        'task': 'notifications.tasks.retry_failed_notifications',
        'schedule': crontab(minute=0, hour='*/12'),  # Every 12 hours
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

