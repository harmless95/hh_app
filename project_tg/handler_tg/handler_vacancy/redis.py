import json
import asyncio

from aiogram import Bot

from dependencies.redis_conn import redis_client, redis_channel
from core.config import logger


async def get_redis(bot: Bot):
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(redis_channel)
    logger.info(f"Subscribed to {redis_channel}")

    try:
        async for message in pubsub.listen():
            logger.info(f"Raw message from Redis: {message}")
            if message["type"] == "message":

                data_app = json.loads(message["data"])
                chat_id = data_app.get("chat_id")
                vacancies = data_app.get("data")
                logger.info("Result app: %s", data_app)
                if not chat_id:
                    continue
                if isinstance(vacancies, list):
                    for item in vacancies[:10]:
                        text_vac = (
                            f"🔹 <b>{item.get('name_vacancy', 'Без названия')}</b>\n"
                            f"🏢 Компания: {item.get('name_company', 'Не указана')}\n"
                            f"🔗 <a href='{item.get('link', '#')}'>Перейти к вакансии</a>"
                        )
                        await bot.send_message(
                            chat_id=chat_id,
                            text=text_vac,
                            parse_mode="HTML",
                        )
                        await asyncio.sleep(0.5)
                else:
                    await bot.send_message(chat_id=chat_id, text=str(vacancies))

    except Exception as e:
        logger.error(f"Ошибка Redis: {e}")
    finally:
        await pubsub.unsubscribe(redis_channel)
    await asyncio.sleep(0.1)
