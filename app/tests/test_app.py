import json
import pytest
from sqlalchemy import select
from unittest.mock import AsyncMock

from core.model import VacancyData

from tests.fixture_db import ac, db_session, override_db, setup_db

from tests.fixture_taskiq import patch_taskiq

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
    assert response.json() == {"saved": 1}

    # идем в БД через тестовую сессию и смотрим, что запись реально появилась

    result = await db_session.execute(
        select(VacancyData).where(VacancyData.id_vacancy == 777)
    )
    vacancy = result.scalar_one_or_none()
    assert vacancy is not None
    assert vacancy.name_vacancy == "test_name"


async def test_get_vacancy(ac, db_session, mocker, patch_taskiq):
    # Подменяем публикацию в редис на AsyncMock
    #  Патчу redis_client именно в том модуле, где он используется
    # 1. Мокаем публикацию в Redis
    mock_publish = mocker.patch(
        "api.Dependencies.queue_data.redis_client.publish",
        new_callable=AsyncMock,
    )

    # 2. Мокаем health_checker.get_system_status()
    mock_health_status = {
        "components": {
            "redis": {
                "available": True,  # Ключевой момент: Redis доступен
                "status": "healthy",
                "latency_ms": 1.5,
            },
            "worker": {"available": True, "queue_size": 0, "workers_count": 2},
            "database": {"available": True, "status": "healthy"},
        },
        "overall_status": "healthy",
    }

    mocker.patch(
        "api.routers.health_checker.get_system_status",
        new_callable=AsyncMock,
        return_value=mock_health_status,
    )

    # 3. Просто мокаем kiq, чтобы он ничего не делал
    mock_kiq = mocker.patch(
        "api.routers.create_tasks.kiq",  # путь к kiq в роутере
        new_callable=AsyncMock,
        return_value=None,
    )

    data_tg = {
        "chat": {"id": 111},
        "user_id": 1,
        "request_id": "22",
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
    assert response.json() == {"saved": 1}

    await db_session.flush()

    response_tg = await ac.post("/v1/data/tg/", json=data_tg)
    assert response_tg.status_code == 200
    assert response_tg.json() == {
        "estimated_time": "1-3 секунды",
        "message": "Ваш запрос принят и обрабатывается",
        "request_id": "22",
        "status": "processing",
    }

    # Проверяем, что kiq был вызван один раз
    mock_kiq.assert_called_once()

    # Получаем аргументы вызова
    call_args = mock_kiq.call_args
    passed_data_tg = call_args[0][0]  # первый аргумент

    # Проверяем атрибуты объекта DataTG (не по индексам!)
    assert passed_data_tg.chat.id == 111
    assert passed_data_tg.user_id == "1"  # обратите внимание: может быть строка
    assert passed_data_tg.request_id == "22"
    assert passed_data_tg.text == ["python"]
