import redis.asyncio as redis
import ssl
import os

FULL_REDIS_URL = str(os.getenv("REDIS__URL"))
redis_channel = "tasks_vacancy"

redis_kwargs = {
    "decode_responses": True,
}

if FULL_REDIS_URL.startswith("rediss"):
    redis_kwargs.update({"ssl_cert_reqs": ssl.CERT_NONE})

redis_client = redis.from_url(
    FULL_REDIS_URL,
    **redis_kwargs,
)
