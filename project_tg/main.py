import asyncio
import os
import uvicorn

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from fastapi import FastAPI

from handler_tg.handler_vacancy.redis import get_redis
from handler_tg.router_inline_keyboard import router
from core.config import setting, logger

TG_TOKEN = setting.config_tg.token
TG_PORT = setting.config_tg.port


bot = Bot(token=TG_TOKEN)
dp = Dispatcher()
dp.include_router(router=router)
app_health = FastAPI()


@app_health.get("/")
def health():
    return {"status": "bot is running"}


def run_health_server():
    # Render передает порт в переменной PORT
    port = int(TG_PORT)
    uvicorn.run(app_health, host="0.0.0.0", port=port)


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


# @dp.message(F.text)
# async def command_text(message: Message):
#     await message.answer(f"Ищу вакансии по навыку: {message.text}...")
#     result_app = await handler_message(message=message)
#     await message.answer(result_app)


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
