import pytest
from sqlalchemy import select
from core.model import VacancyData

from tests.test_db import ac, db_session, override_db, setup_db

pytestmark = pytest.mark.asyncio(scope="session")


async def test_connect(ac):
    response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "bot is running"}


async def test_save_db(ac, db_session):
    data = [
        {
            "id_vacancy": 777,
            "name_vacancy": "test_name",
            "name_company": "test_company",
            "link": "tests link",
            "skills": [
                "test_skill_1",
                "test_skill_2",
            ],
        }
    ]

    response = await ac.post("/v1/data/", json=data)
    assert response.status_code == 201
    assert response.json() == "Completed"

    # 2. ПРОВЕРКА: идем в БД через тестовую сессию и смотрим, что запись реально появилась

    result = await db_session.execute(
        select(VacancyData).where(VacancyData.id_vacancy == 777)
    )
    vacancy = result.scalar_one_or_none()
    assert vacancy is not None
    assert vacancy.name_vacancy == "test_name"
