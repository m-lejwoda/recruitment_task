import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recruitment_task.settings')

app = Celery('recruitment_task',
             broker='redis://satagro_redis:6379/0',
             backend='redis://satagro_redis:6379/0',)

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks(['satagro'])

app.conf.beat_schedule = {
    "task_get_meteo_warnings_every_minute": {
        "task": "satagro.tasks.get_meteo_warnings",
        "schedule": 60.0,
    },
    "task_move_old_meteo_warnings_to_archive_every_hour": {
        "task": "satagro.tasks.move_old_meteo_warnings_to_archive",
        'schedule': crontab(minute=1, hour='*'),
    },
}