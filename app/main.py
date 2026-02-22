import asyncio
import os
import logging

import uvicorn
from fastapi import FastAPI

import redis.asyncio as redis

from api.routers import router

logger = logging.getLogger("FastAPI")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=6379,
    decode_responses=True,
)

app = FastAPI()
app.include_router(router=router)


@app.get("/")
async def get_hello():
    return {
        "message": "Hello",
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
    )
