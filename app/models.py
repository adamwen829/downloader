import time

from app.config import BLACKLIST_EXPIRE_TIME
from app.utils import get_redis_client

r_cli = get_redis_client()


def create_task(key, value_dict):
    enqueue('task_queue', key)
    return r_cli.hmset(key, value_dict)


def set_task_success(key, content_hash):
    dequeue('task_queue', key)
    enqueue('done_queue', key)
    return _update_task(key, {'status': 'done', 'downloaded_time': time.time(), 'content_hash': content_hash})


def set_task_fail(key):
    dequeue('task_queue', key)
    enqueue('failed_queue', key)
    return _update_task(key, {'status': 'failed', 'url': key})


def update_download_progress(key, downloaded):
    return _update_task(key, {'downloaded': downloaded})


def _update_task(key, value_dict):
    return r_cli.hmset(key, value_dict)


def get_task(key):
    return r_cli.hgetall(key)


def enqueue(queue_name, task_key):
    return r_cli.sadd(queue_name, task_key)


def dequeue(queue_name, task_key):
    return r_cli.srem(queue_name, task_key)


def get_tasks_by_status(status):
    status_queue_name = {
        'done': 'done_queue',
        'failed': 'failed_queue',
        'ongoing': 'task_queue'
    }
    key = status_queue_name.get(status, '')
    return r_cli.smembers(key)


def is_duplicated_task(key):
    return r_cli.sismember('task_queue', key) or \
        r_cli.sismember('failed_queue', key) or \
        r_cli.sismember('done_queue', key)


def set_blacklist_domain(domain):
    return r_cli.set(domain, '0', ex=BLACKLIST_EXPIRE_TIME)


def is_blacklisted(domain):
    return True if r_cli.get(domain) else False
