import asyncio
import time
from typing import Annotated, List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.Dependencies import data_save_db, create_tasks, health_checker
from core.model import help_session, Vacancy, DataTG
from core.config import logger

router = APIRouter(prefix="/v1/data", tags=["Vacancy"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def save_data(
    session: Annotated[AsyncSession, Depends(help_session.get_session)],
    data_vacancy: List[Vacancy],
):
    logger.info(f"Save data: %s vacancies", len(data_vacancy))
    try:
        result_save = await data_save_db(
            session=session,
            data=data_vacancy,
        )
        logger.info(f"Successfully saved {result_save.get('saved', 0)} new vacancies")
        return result_save

    except HTTPException:
        # Перевыбрасываем HTTP исключения
        raise

    except asyncio.TimeoutError:
        logger.error("Database timeout while saving vacancies", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Database operation timeout",
        )

    except Exception as ex:
        logger.error(f"Unexpected error while saving vacancies", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save data: {str(ex)}",
        )


@router.post("/tg/")
async def get_vacancy(
    data_tg: DataTG,
):
    start = time.time()
    log_extra = {
        "user_id": data_tg.user_id,
        "request_id": data_tg.request_id,
        "chat_id": data_tg.chat.id if data_tg.chat else None,
    }
    logger.info(
        "Data obtained from TG.: %s",
        data_tg,
        extra=log_extra,
    )
    # 1. Проверяем здоровье системы
    system_status = await health_checker.get_system_status()

    # 2. В зависимости от статуса - разная стратегия

    # Случай 1: Redis не работает (критично)
    if system_status["components"]["redis"]["available"] == False:
        duration_ms = (time.time() - start) * 1000
        logger.error(
            "Redis unavailable, cannot process request",
            extra={
                **log_extra,
                "duration_ms": duration_ms,
                "redis_status": system_status["components"]["redis"]["status"],
            },
        )
        return {
            "status": "error",
            "message": "Технические работы. Пожалуйста, попробуйте позже.",
            "details": "Сервис обработки временно недоступен",
            "code": "SERVICE_UNAVAILABLE",
        }

    try:
        await create_tasks.kiq(data_tg)
        duration_ms = (time.time() - start) * 1000
        logger.info(
            f"Task queued successfully",
            extra={
                **log_extra,
                "duration_ms": duration_ms,
                "queue_size": system_status["components"]["worker"].get(
                    "queue_size", 0
                ),
            },
        )

        return {
            "status": "processing",
            "message": "Ваш запрос принят и обрабатывается",
            "request_id": data_tg.request_id,
            "estimated_time": "1-3 секунды",
        }

    except Exception as e:
        duration_ms = (time.time() - start) * 1000
        logger.error(
            f"Failed to send task to queue: {type(e).__name__}: {e}",
            exc_info=True,
            extra={
                **log_extra,
                "duration_ms": duration_ms,
                "error_type": type(e).__name__,
            },
        )

        return {
            "status": "error",
            "message": "Не удалось обработать запрос. Пожалуйста, попробуйте позже.",
            "code": "QUEUE_ERROR",
            "request_id": data_tg.request_id,
        }
