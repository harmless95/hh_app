import asyncio
import os

import uvicorn
from fastapi import FastAPI

from api.routers import router
from api.Dependencies.ping_server import ping_server
from core.config import logger

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")


app = FastAPI()
app.include_router(router=router)


@app.api_route("/", methods=["GET", "HEAD"])
async def get_check():
    logger.info("Check app")
    return {
        "status": "bot is running",
    }


async def main():
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
    )
    server = uvicorn.Server(config=config)
    await asyncio.gather(
        server.serve(),
        ping_server(),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service stopped")
