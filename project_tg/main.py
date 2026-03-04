import asyncio
import os
import logging
import httpx
import uvicorn

from aiogram import Bot, Dispatcher, html, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from fastapi import FastAPI

TG_TOKEN = os.getenv("TG_TOKEN")
url_app = os.getenv("URL_APP", "http://fastapi_app:8000/v1/data/")
TG_PORT = os.getenv("TG_PORT", 8000)

logger = logging.getLogger("TG_app")

bot = Bot(token=TG_TOKEN)
dp = Dispatcher()
app_health = FastAPI()


@app_health.get("/")
def health():
    return {"status": "bot is running"}


def run_health_server():
    # Render передает порт в переменной PORT
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app_health, host="0.0.0.0", port=port)


async def get_vac(message: Message):
    text = message.text
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url=url_app, json=text)
            logger.warning("Status: %s", response.status_code)
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
                await asyncio.sleep(0.5)
    except Exception as e:
        logging.error(f"Error fetching vacancies: {e}")
        await message.answer("Ошибка при получении вакансий.")


@dp.message(CommandStart())
async def command_start(message: Message):
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


async def run_bot():
    await dp.start_polling(bot)


async def main():
    config = uvicorn.Config(
        app_health,
        host="0.0.0.0",
        port=int(TG_PORT),
    )
    server = uvicorn.Server(config)
    await asyncio.gather(
        server.serve(),
        run_bot(),
    )


if __name__ == "__main__":
    asyncio.run(main())
