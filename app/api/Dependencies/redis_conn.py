import redis.asyncio as redis
import ssl

from app.core.config import setting

redis_channel = setting.redis.channel
FULL_REDIS_URL = setting.redis.url

redis_kwargs = {
    "decode_responses": True,
}

if FULL_REDIS_URL.startswith("rediss"):
    redis_kwargs.update({"ssl_cert_reqs": ssl.CERT_NONE})

redis_client = redis.from_url(
    FULL_REDIS_URL,
    **redis_kwargs,
)
