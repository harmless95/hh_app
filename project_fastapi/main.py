import asyncio
import os

import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import redis.asyncio as redis

app = FastAPI()
REDIS_HOST = os.getenv("REDIS_HOST", "redis")

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


@app.get("/parse")
async def get_parse():
    print("Эндпоинт вызван")

    async def message_redis():
        yield "connect"
        pub_sub = redis_client.pubsub()

        await pub_sub.subscribe("vacancy_hh")
        print("Coonect")
        try:
            async for message in pub_sub.listen():
                print("Слушаю")
                if message["type"] == "message":
                    print(message["data"])
                    data = (
                        message["data"].decode("utf-8")
                        if isinstance(message["data"], bytes)
                        else message["data"]
                    )
                    yield data
                    await asyncio.sleep(1)
        except Exception as ex:
            print(f"Error: {ex}")
            yield f"Ошибка: {ex}"
        finally:
            await pub_sub.unsubscribe("vacancy_hh")
            await pub_sub.close()

    return StreamingResponse(message_redis(), media_type="text/event-stream")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
    )
