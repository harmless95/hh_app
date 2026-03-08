import redis.asyncio as redis
import ssl

from core.config import setting

REDIS_HOST = setting.redis.host
REDIS_PASSWORD = setting.redis.password
redis_channel = "tasks_vacancy"
FULL_REDIS_URL = f"rediss://default:{REDIS_PASSWORD}@{REDIS_HOST}:6379/0"

redis_client = redis.from_url(
    FULL_REDIS_URL,
    ssl_cert_reqs=ssl.CERT_NONE,
    decode_responses=True,
)
