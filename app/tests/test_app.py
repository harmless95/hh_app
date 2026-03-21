import pytest
import asyncio
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy import delete

from main import app

from core.model import help_session, VacancyData, HelperDB

client = TestClient(app=app)
pytestmark = pytest.mark.asyncio(scope="session")

test_helper = HelperDB(
    url="postgresql+asyncpg://user:pass@localhost:5433/test_db",
    echo=False,
    echo_pool=False,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)


@pytest.fixture(scope="session")
def event_loop():
    """Создает экземпляр event loop один раз на всю сессию тестов."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_session():
    """Фикстура для получения сессии в самих тестах"""
    async with test_helper.get_session_context() as session:
        yield session
        await session.execute(delete(VacancyData).where(VacancyData.id_vacancy == 777))
        await session.commit()


@pytest_asyncio.fixture(autouse=True)
async def override_db():
    """Автоматически подменяет БД во всем приложении на время тестов"""
    # Если в роутах используется help_session.get_session
    app.dependency_overrides[help_session.get_session] = test_helper.get_session
    yield
    app.dependency_overrides.pop(help_session.get_session, None)


@pytest_asyncio.fixture
async def ac():
    """Асинхронный клиент для запросов"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest_asyncio.fixture(autouse=True)
async def clean_db():
    # Перед каждым тестом очищаем таблицы
    async with test_helper.get_session_context() as session:
        # пример: очистка таблицы
        await session.execute(delete(VacancyData))
        await session.commit()
    yield


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
    from sqlalchemy import select
    from core.model import VacancyData

    result = await db_session.execute(
        select(VacancyData).where(VacancyData.id_vacancy == 777)
    )
    vacancy = result.scalar_one_or_none()
    assert vacancy is not None
    assert vacancy.name_vacancy == "test_name"
