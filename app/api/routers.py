from typing import Annotated, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.Dependencies.crud import data_save_db
from app.api.Dependencies.queue_data import create_tasks
from app.core.model import help_session, Vacancy, DataTG
from app.core.config import logger

router = APIRouter(prefix="/v1/data", tags=["Vacancy"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def save_data(
    session: Annotated[AsyncSession, Depends(help_session.get_session)],
    data_vacancy: List[Vacancy],
):
    logger.info("Save data")
    result_save = await data_save_db(
        session=session,
        data=data_vacancy,
    )
    if not result_save:
        logger.warning("Failed to save data")
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
