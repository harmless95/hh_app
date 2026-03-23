import json
import pytest
from sqlalchemy import select
from unittest.mock import AsyncMock

from core.model import VacancyData
from tests.test_db import ac, db_session, override_db, setup_db
import api.routers as routers_module
from api.Dependencies.queue_data import create_tasks

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

    # идем в БД через тестовую сессию и смотрим, что запись реально появилась

    result = await db_session.execute(
        select(VacancyData).where(VacancyData.id_vacancy == 777)
    )
    vacancy = result.scalar_one_or_none()
    assert vacancy is not None
    assert vacancy.name_vacancy == "test_name"


async def test_get_vacancy(ac, db_session, mocker):
    # Подменяем публикацию в редис на AsyncMock
    #  Патчу redis_client именно в том модуле, где он используется
    mock_publish = mocker.patch(
        "api.Dependencies.queue_data.redis_client.publish",
        new_callable=AsyncMock,
    )

    async def mock_kiq_logic(body, **_):
        return await create_tasks(body, session=db_session)

    mocker.patch.object(
        routers_module.create_tasks,
        "kiq",
        side_effect=mock_kiq_logic,
    )

    data_tg = {
        "chat": {"id": 111},
        "text": [
            "python",
        ],
    }

    data_app = [
        {
            "id_vacancy": 777,
            "name_vacancy": "test_name",
            "name_company": "test_company",
            "link": "tests link",
            "skills": [
                "python",
            ],
        }
    ]
    response = await ac.post("/v1/data/", json=data_app)
    assert response.status_code == 201
    assert response.json() == "Completed"

    await db_session.flush()

    response_tg = await ac.post("/v1/data/tg/", json=data_tg)
    assert response_tg.status_code == 200
    assert response_tg.json() == {
        "status": "Обработка данных",
    }

    mock_publish.assert_called_once()

    args, _ = mock_publish.call_args

    # channel = args[0]
    payload = json.loads(args[1])
    #
    # assert channel == redis_channel
    assert payload["chat_id"] == 111
    assert payload["data"][0]["name_vacancy"] == "test_name"
    assert payload["data"][0]["name_company"] == "test_company"
    assert payload["data"][0]["link"] == "tests link"
