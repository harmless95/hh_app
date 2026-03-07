import asyncio
import os
import logging
import httpx
import uvicorn
import json

from aiogram import Bot, Dispatcher, html, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from fastapi import FastAPI

from dependencies.redis_conn import redis_client, redis_channel

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


async def handler_message(message: Message):

    data_json = message.model_dump()
    logger.error("Data TG: %s, %s", type(data_json), data_json)
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url=url_app, json=data_json)
            logger.error("Resp: %s", response)
            if response.status_code == 200:
                return "Сообщение обработанно"

            logger.warning("API Error %s: %s", response.status_code, response.text)
            return "Не удалось обработать данные"

    except httpx.ReadTimeout:
        return "Сервер слишком долго думал, но мы продолжаем обработку"
    except Exception as ex:
        logger.exception("Webhook sending failed")
        return "Ошибка связи с сервером"


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
    result_app = await handler_message(message=message)
    await message.answer(result_app)


async def run_bot():
    redis_tasks = asyncio.create_task(get_redis(bot))
    try:
        await dp.start_polling(bot)
    finally:
        redis_tasks.cancel()


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
