import redis.asyncio as redis
import os

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
redis_channel = "tasks_vacancy"

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=6379,
    decode_responses=True,
)
