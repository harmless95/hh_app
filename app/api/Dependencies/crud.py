from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from core.model import Vacancy, VacancyData
from core.config import logger


async def data_save_db(session: AsyncSession, data: List[Vacancy]):
    if not data:
        return {"saved": 0}

        # Проверяем дубликаты
    valid_ids = [v.id_vacancy for v in data if v.id_vacancy]
    stmt = select(VacancyData.id_vacancy).where(VacancyData.id_vacancy.in_(valid_ids))
    result = await session.execute(stmt)
    existing_ids = set(result.scalars().all())

    # Подготавливаем новые данные
    new_vacancies = []
    for vacancy in data:
        if vacancy.id_vacancy not in existing_ids:
            new_vacancies.append(
                {
                    "id_vacancy": vacancy.id_vacancy,
                    "name_vacancy": vacancy.name_vacancy.lower(),
                    "name_company": (
                        vacancy.name_company.lower() if vacancy.name_company else None
                    ),
                    "link": vacancy.link,
                    "skills": [skill.lower() for skill in (vacancy.skills or [])],
                }
            )

    if not new_vacancies:
        return {"saved": 0}

    # Массовая вставка (один запрос!)
    try:
        stmt = insert(VacancyData).values(new_vacancies)
        # Если есть уникальный индекс по id_vacancy:
        stmt = stmt.on_conflict_do_nothing()

        await session.execute(stmt)
        await session.commit()

        logger.info(f"Bulk inserted {len(new_vacancies)} vacancies")
        return {"saved": len(new_vacancies)}

    except Exception as e:
        await session.rollback()
        logger.error(f"Bulk insert failed", exc_info=True)
        raise
