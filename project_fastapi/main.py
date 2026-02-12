import asyncio
import os
import logging
from typing import Annotated

import uvicorn
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

import redis.asyncio as redis

from core.schema_vacancy import Vacancy
from core.helper_db import help_session

logger = logging.getLogger("FastAPI")
app = FastAPI()
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=6379,
    decode_responses=True,
)


@app.get("/")
async def get_hello():
    return {
        "message": "Hello",
    }


#
# @app.get("/parse")
# async def get_parse():
#


@app.post("/")
async def search_vacancy(
    session: Annotated[AsyncSession, Depends(help_session.get_session)],
    data: Vacancy,
):
    # 1. К Pydantic-модели обращаемся через точку, а не как к словарю
    url = (
        f"https://abakan.hh.ru/search/vacancy?text={data.text}"
        f"&work_format={data.work_format}"
        f"&items_on_page={data.items_on_page}"
        f"&experience={data.experience}"
    )

    tg_id = 5103681164

    # 2. Правильный SQL запрос с ON CONFLICT (чтобы обновлять URL, если юзер уже есть)
    query = text("""
           INSERT INTO users (url, telegram_id) 
           VALUES (:url, :tg_id)
           ON CONFLICT (telegram_id) DO UPDATE SET url = EXCLUDED.url
       """)

    try:
        # 3. Выполняем и ОБЯЗАТЕЛЬНО комитим
        await session.execute(query, {"url": url, "tg_id": tg_id})
        await session.commit()
        return {"status": "success", "url": url}
    except Exception as e:
        await session.rollback()
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
    )
