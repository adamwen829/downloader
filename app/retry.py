import json
import time

from celery import Celery
from celery.utils.log import get_task_logger

from app.config import TASK_MAX_TIMEOUT
from app.models import get_tasks_by_status, dequeue, get_task, set_task_fail
from app.offline import download

app = Celery('offline', broker='redis://localhost:6379/2')
app.config_from_object('app.celery_config')
logger = get_task_logger(__name__)


@app.task
def retry_failed_tasks():
    failed_tasks = get_tasks_by_status('failed')
    logger.info('retry {0}'.format('\n'.join(failed_tasks)))
    for url in failed_tasks:
        dequeue('failed_queue', url)
        download.delay(json.dumps({'url': url}))


@app.task
def stop_no_response_tasks():
    ongoing_tasks = get_tasks_by_status('ongoing')
    for url in ongoing_tasks:
        task_detail = get_task(url)
        # if task_detail.get('created') - time.time() > TASK_MAX_TIMEOUT:
        if time.time() - task_detail.get('created') > 1:
            set_task_fail(url)
