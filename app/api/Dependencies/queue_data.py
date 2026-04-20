import json
import taskiq_redis
from taskiq import TaskiqDepends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, cast, Text
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY

from api.Dependencies.redis_conn import redis_client, redis_channel, FULL_REDIS_URL
from core.config import logger
from core.model import help_session, VacancyData, VacancyTG, DataTG

broker = taskiq_redis.ListQueueBroker(FULL_REDIS_URL)


async def send_error_to_redis(body: DataTG, error_message: str):
    """Отправляет сообщение об ошибке в Redis"""

    log_extra = {
        "user_id": body.user_id,
        "request_id": body.request_id,
        "chat_id": body.chat.id if body.chat else None,
    }

    try:
        error_payload = json.dumps(
            {
                "data": error_message,
                "chat_id": body.chat.id,
                "error": True,
                "request_id": body.request_id,
            },
            ensure_ascii=False,
        )

        await asyncio.wait_for(
            redis_client.publish(redis_channel, error_payload), timeout=3.0
        )
        logger.debug("Error message sent to Redis", extra=log_extra)

    except asyncio.TimeoutError:
        logger.error("Timeout sending error to Redis", extra=log_extra)

    except Exception as redis_error:
        logger.error(
            f"Failed to send error to Redis: {redis_error}",
            exc_info=True,
            extra=log_extra,
        )


@broker.task
async def create_tasks(
    body: DataTG,
    session: AsyncSession = TaskiqDepends(help_session.get_session),
):
    try:
        data_tg = body.text
        if not data_tg:
            return
        if isinstance(data_tg, list):
            search_skills = [skill.lower() for skill in data_tg]
            stmt = select(VacancyData).where(
                VacancyData.skills.contains(cast(search_skills, PG_ARRAY(Text)))
            )
        else:
            stmt = select(VacancyData).where(VacancyData.skills.any(data_tg.lower()))
        result = await session.execute(stmt)
        list_result = result.scalars().all()

        if list_result:
            data_vac = [
                VacancyTG.model_validate(item).model_dump() for item in list_result
            ]
            logger.info("Data found and sent to redis: %s", len(data_vac))
        else:
            search_terms = ",".join(data_tg) if isinstance(data_tg, list) else data_tg
            data_vac = f"Nothing found for your search query: {search_terms}"
            logger.info(
                "Nothing found for your search query: %s .", data_tg, extra=log_extra
            )

        data_dict = {
            "data": data_vac,
            "chat_id": body.chat.id,
        }
        payload = json.dumps(data_dict, ensure_ascii=False)
        try:
            await asyncio.wait_for(redis_client.ping(), timeout=2.0)
        except asyncio.TimeoutError:
            logger.error("Redis ping timeout", extra=log_extra)
            return
        except Exception as e:
            logger.error(f"Redis connection lost: {e}", extra=log_extra)
            return

        await asyncio.wait_for(
            redis_client.publish(redis_channel, payload), timeout=5.0
        )
        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            f"Task completed in {duration_ms:.2f}ms",
            extra={**log_extra, "duration_ms": duration_ms},
        )

    except asyncio.TimeoutError:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            "Task timeout",
            exc_info=True,
            extra={**log_extra, "duration_ms": duration_ms},
        )

        await send_error_to_redis(body, "Превышено время ожидания ответа от сервера")

    except Exception:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            "Error in TaskIQ worker",
            exc_info=True,
            extra={**log_extra, "duration_ms": duration_ms},
        )

        await send_error_to_redis(
            body,
            "Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже.",
        )
