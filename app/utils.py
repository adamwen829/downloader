import hashlib

from redis import ConnectionPool
from redis import StrictRedis

from app.config import REDIS_CONFIG


def get_redis_client():
    pool = ConnectionPool(**REDIS_CONFIG)
    return StrictRedis(connection_pool=pool)


def get_content_hash(content):
    return hashlib.sha256(content).hexdigest()
