from typing import Annotated, List
from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud import data_save_db, get_tg
from core.model import help_session, Vacancy
from api.Dependencies.crud import data_save_db
from api.Dependencies.queue_data import create_tasks
from core.model import help_session, Vacancy, DataTG
from core.config import logger

router = APIRouter(prefix="/v1/data", tags=["Vacancy"])
logger = logging.getLogger("FastAPI")


@router.post("/")
async def save_data(
    session: Annotated[AsyncSession, Depends(help_session.get_session)],
    data_vacancy: List[Vacancy],
):
    result_save = await data_save_db(
        session=session,
        data=data_vacancy,
    )
    return result_save


@router.post("/tg/")
async def get_vacancy(
    data_tg: DataTG = Body(),
):
    logger.info("Data obtained from TG.: %s", data_tg)
    await create_tasks.kiq(data_tg)
    return {
        "status": "Обработка данных",
    }
