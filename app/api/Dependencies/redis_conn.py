import redis.asyncio as redis

from core.config import setting

REDIS_HOST = setting.redis.host
REDIS_PASSWORD = setting.redis.password
redis_channel = "tasks_vacancy"

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=6379,
    decode_responses=True,
)
