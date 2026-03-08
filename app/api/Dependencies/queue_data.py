import json
import taskiq_redis
from taskiq import TaskiqDepends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.Dependencies.redis_conn import (
    REDIS_HOST,
    REDIS_PASSWORD,
    redis_client,
    redis_channel,
)
from core.config import logger
from core.model import help_session, VacancyData, VacancyTG, DataTG

REDIS_URL = f"rediss://default:{REDIS_PASSWORD}@{REDIS_HOST}:6379/0"
broker = taskiq_redis.ListQueueBroker(REDIS_URL)


@broker.task
async def create_tasks(
    body: DataTG,
    session: AsyncSession = TaskiqDepends(help_session.get_session),
):
    try:
        data_tg = body.text
        if not data_tg:
            return
        stmt = select(VacancyData).where(VacancyData.skills.any(data_tg.lower()))
        result = await session.execute(stmt)
        list_result = result.scalars().all()

        if list_result:
            data_vac = [
                VacancyTG.model_validate(item).model_dump() for item in list_result
            ]
            logger.info("Data found and sent to redis: %s", len(data_vac))
        else:
            data_vac = f"Nothing found for your search query: {data_tg}"
            logger.info("Nothing found for your search query: %s .", data_tg)

        data_dict = {
            "data": data_vac,
            "chat_id": body.chat.id,
        }
        payload = json.dumps(data_dict, ensure_ascii=False)
        await redis_client.publish(redis_channel, payload)

    except Exception:
        logger.exception("Error in TaskIQ worker")
