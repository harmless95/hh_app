import redis.asyncio as redis
import ssl

from core.config import setting

redis_channel = "tasks_vacancy"
FULL_REDIS_URL = setting.redis.url

redis_client = redis.from_url(
    FULL_REDIS_URL,
    ssl_cert_reqs=ssl.CERT_NONE,
    decode_responses=True,
)
