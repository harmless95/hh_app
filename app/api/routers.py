from typing import Annotated, List
from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud import data_save_db
from core.helper_db import help_session
from core.schema_vacancy import Vacancy

from api.crud import get_tg

router = APIRouter(prefix="/v1/data", tags=["Vacancy"])


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
    session: Annotated[AsyncSession, Depends(help_session.get_session)],
    data_tg: str = Body(),
):
    list_vacancy = await get_tg(
        session=session,
        data_tg=data_tg,
    )
    return list_vacancy
