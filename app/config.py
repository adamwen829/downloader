import os

WHITE_LIST = ['image', 'video']
RESOURCE_MAX_SIZE = 5 * (1 << 20)
TASK_MAX_TIMEOUT = 3600
DOWNLOAD_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'download_resource')
BLACKLIST_EXPIRE_TIME = 3600

APPLICATION_CONF = {
    'debug': False,
}

REDIS_CONFIG = {
    'host': os.environ.get('REDIS_HOST', '127.0.0.1'),
    'port': 6379,
    'db': 1,
    'max_connections': 20,
    'socket_timeout': 1,
}
