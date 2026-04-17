from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# from celery.schedules import crontab, solar
from datetime import timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ed.settings")


app = Celery("ed")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.task_track_started = True
app.conf.worker_send_task_events = True

app.conf.beat_schedule = {
    "process-rma-email-every-48-hours": {
        "task": "common.tasks.process_rma_email",
        "schedule": timedelta(hours=48),  # Every 48 hours
    },
    # 'clear-user-auth-activity-each-90-days': {
    #     'task': 'account.tasks.clear_user_auth_activity',
    #     'schedule': timedelta(days=1),  # Every 1 day, 2 hours, and 30 minutes
    # },
    # 'clear-verification-token-every-24-hours': {
    #     'task': 'myapp.tasks.clear_verification_token',
    #     'schedule': crontab(hour=0, minute=0),
    # },
    # 'task-every-30-minutes': {
    #     'task': 'myapp.tasks.some_task',
    #     'schedule': 1800.0,  # 30 minutes
    # },
    # 'task-every-5-seconds': {
    #     'task': 'myapp.tasks.some_task',
    #     'schedule': 5.0,  # 5 seconds
    # },
    # 'task-at-sunrise': {
    #     'task': 'myapp.tasks.some_task',
    #     'schedule': solar('sunrise', latitude=40.7128, longitude=-74.0060),
    # },
    # 'task-at-sunset': {
    #     'task': 'myapp.tasks.some_task',
    #     'schedule': solar('sunset', latitude=40.7128, longitude=-74.0060),
    # },
    # 'custom-schedule-task': {
    #     'task': 'myapp.tasks.some_task',
    #     'schedule': timedelta(days=1, hours=2, minutes=30),  # Every 1 day, 2 hours, and 30 minutes
    # },
}
