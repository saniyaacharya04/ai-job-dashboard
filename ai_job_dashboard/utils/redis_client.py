import redis, os
from ai_job_dashboard.utils.logger import get_logger
logger = get_logger("RedisClient")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
rc = redis.from_url(REDIS_URL)

def set_bytes(key, b, ex=3600):
    try:
        return rc.set(key, b, ex=ex)
    except Exception as e:
        logger.exception("redis set failed")
        return False

def get_bytes(key):
    try:
        v = rc.get(key)
        return v
    except Exception:
        return None
