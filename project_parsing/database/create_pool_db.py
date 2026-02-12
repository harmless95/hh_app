import logging
import os

import asyncpg

logger = logging.getLogger("PostgresDB")

POSTGRES_USER = os.getenv("POSTGRES_USER", "user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "pass")
POST_HOST = os.getenv("POST_DB", "localhost")
POSTGRES_DB = os.getenv("POSTGRES_DB", "hh_base")


class DatabasePG:
    def __init__(self):
        self._pool = None

    async def get_pool(self):
        self._pool = await asyncpg.create_pool(
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=POSTGRES_DB,
            host=POST_HOST,
            min_size=5,
            max_size=10,
        )
        return self._pool

    async def pool_async(self, data: list):
        pool = await self.get_pool()
        try:
            async with pool.acquire() as conn:
                query = """
                               INSERT INTO vacancy_data (id_vacancy, name_vacancy, name_company, link, skills)
                               VALUES ($1, $2, $3, $4, $5)
                               ON CONFLICT (link) DO NOTHING;
                       """

                list_data = [
                    (
                        item.get("id_vacancy"),
                        item.get("Название вакансии"),
                        item.get("Название компании"),
                        item.get("Сcылка"),
                        item.get("skills"),
                    )
                    for item in data
                ]

                await conn.executemany(query, list_data)
                logger.info(f"Successfully inserted {len(list_data)} records")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")

    async def check_url(self, id_telegram: int):
        pool = await self.get_pool()
        try:
            async with pool.acquire() as conn:
                query = """
                    SELECT url FROM users WHERE telegram_id=$1
                """

                result_check = await conn.fetchval(query, id_telegram)
                return result_check
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return None

    async def close(self):
        if self._pool:
            await self._pool.close()
            logger.info("Database pool closed")


db_pg = DatabasePG()
