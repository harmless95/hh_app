import logging
import os

import asyncpg

logger = logging.getLogger("PostgresDB")

POSTGRES_USER = os.getenv("POSTGRES_USER", "user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "pass")
POST_HOST = os.getenv("POST_DB", "localhost")
POSTGRES_DB = os.getenv("POSTGRES_DB", "hh_base")


async def pool_async(data: list):
    db_pool = None
    try:
        db_pool = await asyncpg.create_pool(
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=POSTGRES_DB,
            host=POST_HOST,
        )
        logger.info("Connected to Database")

        async with db_pool.acquire() as conn:
            query = """
                           INSERT INTO vacancy_data (name_vacancy, name_company, link, skills)
                           VALUES ($1, $2, $3, $4)
                           ON CONFLICT (link) DO NOTHING;
                   """

            list_data = [
                (
                    item.get("Название вакансии"),
                    item.get("Название компании"),
                    item.get("Сcылка"),
                    item.get("skills"),
                )
                for item in data
            ]

            await conn.executemany(query, list_data)
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
    finally:
        if db_pool:
            await db_pool.close()
