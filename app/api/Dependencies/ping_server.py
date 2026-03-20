import asyncio
import httpx

from app.core.config import setting, logger

PING_HOST = setting.ping_app.url


async def ping_server():
    await asyncio.sleep(10)
    async with httpx.AsyncClient() as client:
        while True:
            try:
                await client.get(PING_HOST)
                logger.info("Ping success")
            except Exception as ex:
                logger.error(f"Ping failed: {ex}")
            await asyncio.sleep(600)
