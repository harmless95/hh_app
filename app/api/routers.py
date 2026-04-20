from typing import Annotated, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.Dependencies.crud import data_save_db
from api.Dependencies.queue_data import create_tasks
from api.Dependencies.health_check import health_checker
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
    requests_id = str(uuid4())
    try:
        result_save = await data_save_db(
            session=session,
            data=data_vacancy,
        )
        logger.info(f"Successfully saved {result_save.get('saved', 0)} new vacancies")
        return result_save


@router.post("/tg/")
async def get_vacancy(
    data_tg: DataTG,
):
    logger.info("Data obtained from TG.: %s", data_tg)
    await create_tasks.kiq(data_tg)
    return {
        "status": "Обработка данных",
    }
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

    # # Случай 2: Воркеры не работают (деградация)
    # if not system_status["components"]["worker"]["available"]:
    #     duration_ms = (time.time() - start) * 1000
    #     queue_size = system_status["components"]["worker"].get("queue_size", 0)
    #     logger.warning(
    #         f"No workers available. Queue size: {system_status['components']['worker'].get('queue_size', 0)}",
    #         extra={
    #             **log_extra,
    #             "duration_ms": duration_ms,
    #             "queue_size": queue_size,
    #             "workers_count": system_status["components"]["worker"].get(
    #                 "workers_count", 0
    #             ),
    #         },
    #     )
    #
    #     # Вариант А: Отказать в обработке
    #     return {
    #         "status": "error",
    #         "message": "Сервис обработки временно перегружен. Пожалуйста, попробуйте через несколько минут.",
    #         "details": "Все воркеры заняты или недоступны",
    #         "code": "WORKERS_UNAVAILABLE",
    #     }
