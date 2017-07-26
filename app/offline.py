import os
import json
import time
from urlparse import urlparse

import requests
from celery import Celery, Task
from celery.utils.log import get_task_logger

from app.config import WHITE_LIST, RESOURCE_MAX_SIZE, DOWNLOAD_PATH
from app.models import set_task_success, set_task_fail, create_task, update_download_progress, is_duplicated_task, set_blacklist_domain, is_blacklisted
from app.utils import get_content_hash

app = Celery('offline', broker='redis://localhost:6379/2')
logger = get_task_logger(__name__)

if not os.path.exists(DOWNLOAD_PATH):
    os.makedirs(DOWNLOAD_PATH)


class DownloadTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        set_task_fail(json.loads(args[0]).get('url'))
        return super(DownloadTask, self).on_failure(exc, task_id, args, kwargs, einfo)


@app.task(base=DownloadTask, bind=True)
def download(self, json_url):
    url = json.loads(json_url).get('url')
    if _is_validated_url(url):
        _download(url, self.request.id)


def _download(url, task_id):
    with requests.get(url, stream=True) as res:
        if res.encoding is None:
            res.encoding = 'utf-8'
        if not _is_validated_response(url, res):
            return

        task = {
            'url': url,
            'size': float(res.headers.get('Content-Length')),
            'status': 'init',
            'mimetype': res.headers.get('Content-Type'),
            'created': time.time(),
            'task_id': task_id,
        }
        create_task(url, task)

        content = ''
        for chunk in res.iter_content(chunk_size=None):
            content += chunk
            update_download_progress(url, len(content))

        file_name = url.split('/')[-1]
        file_path = os.path.join(DOWNLOAD_PATH, file_name)
        with open(file_path, 'wb') as fw:
            fw.write(content)

        set_task_success(url, get_content_hash(content))


def _is_validated_url(url):
    if is_duplicated_task(url):
        logger.info('duplicated_task: {0}'.format(url))
        return False
    netloc = urlparse(url).netloc
    if is_blacklisted(netloc):
        set_task_fail(url)
        logger.info('blacklisted domain: {0}'.format(netloc))
        return False
    return True


def _is_validated_response(url, res):
    if res.status_code == 403:
        netloc = urlparse(url).netloc
        set_blacklist_domain(netloc)
        set_task_fail(url)
        logger.info('blacklisted by domain: {0}'.format(netloc))
        return False
    if res.status_code != 200:
        return False
    if res.headers.get('Content-Type', '').split('/')[0] not in WHITE_LIST:
        logger.info('unsupported type: {0}'.format(url))
        return False
    if float(res.headers.get('Content-Length', float('inf'))) > RESOURCE_MAX_SIZE:
        logger.info('resource too large: {0}'.format(url))
        return False
    return True
