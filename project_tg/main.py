import asyncio
import json
import os
import logging

from aiogram import Bot, Dispatcher, html, F
from aiogram.filters import CommandStart
from aiogram.types import Message
import redis.asyncio as redis

TG_TOKEN = os.getenv("TG_TOKEN")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=6379,
    decode_responses=True,
)
logger = logging.getLogger("TG_app")

bot = Bot(token=TG_TOKEN)
dp = Dispatcher()
active_users = set()


async def redis_listen():
    pub_sub = redis_client.pubsub()
    await pub_sub.subscribe("vacancy_hh")
    try:
        async for redis_msg in pub_sub.listen():
            logger.info("Слушаю")
            if redis_msg["type"] == "message":
                logger.info(redis_msg["data"])
                data = json.loads(redis_msg["data"])
                text = (
                    f"🔥 <b>Новая вакансия!</b>\n\n"
                    f"💼 {data.get('Название вакансии')}\n"
                    f"🏢 {data.get('Название компании')}\n"
                    f"🔗 <a href='{data.get('Сcылка')}'>Открыть на HH</a>"
                )
                await asyncio.sleep(0.5)
                for user_id in active_users:
                    try:
                        await bot.send_message(user_id, text, parse_mode="HTML")
                    except Exception as e:
                        logger.error(f"Не смог отправить сообщение {user_id}: {e}")
    finally:
        await pub_sub.close()


@dp.message(CommandStart())
async def command_start(message: Message):
    active_users.add(message.from_user.id)
    await message.answer(
        f"Привет, <b>{message.from_user.full_name}</b>! Теперь я буду присылать тебе вакансии из Redis.",
        parse_mode="HTML",
    )


async def main():
    asyncio.create_task(redis_listen())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
