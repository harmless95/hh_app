import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.main import app

# from core.model import help_session, VacancyData

client = TestClient(app=app)
pytestmark = pytest.mark.asyncio
#
#
# @pytest_asyncio.fixture
# async def clean_test_vacancy():
#
#     async with help_session.get_session_context() as session:
#
#         stmt = delete(VacancyData).where(VacancyData.id_vacancy == 777)
#         await session.execute(stmt)
#         await session.commit()
#
#     yield
#
#     async with help_session.get_session_context() as session:
#         stmt = delete(VacancyData).where(VacancyData.id_vacancy == 777)
#         await session.execute(stmt)
#         await session.commit()


async def test_connect():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "bot is running"}


# async def test_save_db(clean_test_vacancy):
#     data = [
#         {
#             "id_vacancy": 777,
#             "name_vacancy": "test_name",
#             "name_company": "test_company",
#             "link": "tests link",
#             "skills": [
#                 "test_skill_1",
#                 "test_skill_2",
#             ],
#         }
#     ]
#
#     response = client.post("/v1/data/", json=data)
#     assert response.status_code == 201
#     assert response.json() == "Completed"
