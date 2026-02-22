import asyncio
import json
import os
import logging
import httpx

from aiogram import Bot, Dispatcher, html, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

# import redis.asyncio as redis


TG_TOKEN = os.getenv("TG_TOKEN")
# REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

# redis_client = redis.Redis(
#     host=REDIS_HOST,
#     port=6379,
#     decode_responses=True,
# )
logger = logging.getLogger("TG_app")

bot = Bot(token=TG_TOKEN)
dp = Dispatcher()
active_users = set()
url_app = "http://fastapi_app:8000/v1/data/tg/"


async def get_vac(message: Message):
    text = message.text
    async with httpx.AsyncClient() as client:
        response = await client.post(url=url_app, json=text)
        response.raise_for_status()
        vacancies = response.json()
        for item in vacancies[:10]:
            text_vac = (
                f"🔹 <b>{item.get('name_vacancy', 'Без названия')}</b>\n"
                f"🏢 Компания: {item.get('name_company', 'Не указана')}\n"
                f"🔗 <a href='{item.get('link', '#')}'>Перейти к вакансии</a>"
            )
            await message.answer(
                text_vac,
                parse_mode="HTML",
            )
            await asyncio.sleep(1)


@dp.message(CommandStart())
async def command_start(message: Message):
    active_users.add(message.from_user.id)
    await message.answer(
        f"Привет, <b>{message.from_user.full_name}</b>! Укажите по каким навыкам искать?",
        parse_mode="HTML",
    )


@dp.message(Command("stop"))
async def command_stop(
    message: Message,
    state: FSMContext,
):
    await state.clear()
    await message.answer("Все процессы остановились")


@dp.message(F.text)
async def command_text(message: Message):
    await message.answer(f"Ищу вакансии по навыку: {message.text}...")
    await get_vac(message=message)


async def main():
    # asyncio.create_task(redis_listen())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
