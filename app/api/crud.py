from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from core.schema_vacancy import Vacancy
from core.schema_tg import VacancyTG
from core.vacancy_data import VacancyData


async def data_save_db(session: AsyncSession, data: List[Vacancy]):
    id_data_st = [st.id_vacancy for st in data]
    stmt = select(VacancyData).where(VacancyData.id_vacancy.in_(id_data_st))
    result = await session.execute(stmt)
    vac = set(result.scalars().all())

    new_vacancy = []
    for dt in data:
        if dt.id_vacancy in vac:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Invalid {dt.id_vacancy}",
            )
        new_vacancy.append(VacancyData(**dt.model_dump()))
    session.add_all(new_vacancy)
    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при сохранении в БД")
    return "Completed"


async def get_tg(
    session: AsyncSession,
    data_tg: str,
):
    stmt = select(VacancyData).where(VacancyData.skills.any(data_tg))
    result = await session.execute(stmt)
    list_vac = result.scalars().all()
    return [VacancyTG.model_validate(item) for item in list_vac]
