import asyncio
import os

import uvicorn
from fastapi import FastAPI
import redis.asyncio as redis

from api.routers import router
from core.config import logger

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")


app = FastAPI()
app.include_router(router=router)


@app.get("/")
async def get_hello():
    logger.info("Check app")
    return {
        "message": "Hello",
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
    )
