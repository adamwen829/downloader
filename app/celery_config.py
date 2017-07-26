from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'retry_failed': {
        'task': 'app.retry.retry_failed_tasks',
        # 'schedule': crontab(minute=0, hour='*/2'),
        'schedule': crontab(),
    },
    'scan_dead': {
        'task': 'app.retry.stop_no_response_tasks',
        'schedule': crontab(),
    }
}
