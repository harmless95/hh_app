import asyncio
import json
import os
import logging

import redis.asyncio as redis

from playwright.async_api import async_playwright
from database.create_pool_db import db_pg

logger = logging.getLogger("ParseData")

text = "playwright"
work_format = "REMOTE"
items_on_page = "20"
experience = "moreThan6"

# URL = f"https://abakan.hh.ru/search/vacancy?text={text}&work_format={work_format}&items_on_page={items_on_page}&&experience={experience}"


REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=6379,
    decode_responses=True,
)


async def check(id_vac, conn):
    try:
        query = """
                    SELECT * FROM vacancy_data WHERE id_vacancy=$1
                """
        result_check = await conn.fetchrow(query, id_vac)
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None
    return result_check


async def get_hh_page(page, url: str):

    # Переходим по ссылке
    await page.goto(url, wait_until="domcontentloaded")

    # Можно сделать скриншот, чтобы проверить, не вылезла ли капча
    await page.screenshot(path="./resource/hh_check.png")

    # Получаем HTML всей страницы
    content = await page.content()

    vacancy = await page.locator('div[data-qa="vacancy-serp__vacancy"]').all()
    print("Кол-во: ", len(vacancy))
    result = []
    result_id = []
    pool = await db_pg.get_pool()

    async with pool.acquire() as conn:
        for card in vacancy:
            id_vac = await card.locator(
                'div[class="vacancy-card--n77Dj8TY8VIUF0yM font-inter"]'
            ).get_attribute("id")
            print("id", id_vac)
            result_id.append(id_vac)
            check_db = await check(int(id_vac), conn)
            if check_db:
                continue
            titles = await card.locator(
                '[data-qa="serp-item__title-text"]'
            ).text_content()
            company_name = await card.locator(
                '[data-qa="vacancy-serp__vacancy-employer"]'
            ).text_content()
            link_vacancy = await card.locator(
                '[data-qa="serp-item__title"]'
            ).get_attribute("href")

            result.append(
                {
                    "id_vacancy": int(id_vac),
                    "Название вакансии": titles,
                    "Название компании": company_name,
                    "Сcылка": link_vacancy,
                }
            )
        for idx, item in enumerate(result):
            try:
                print(f"Загруженна вакансия: {idx + 1}")
                await page.goto(
                    item.get("Сcылка"),
                    wait_until="domcontentloaded",
                    timeout=15000,
                )
                item["skills"] = await page.locator(
                    '[data-qa="skills-element"]'
                ).all_text_contents()
                logger.info("HOST Reddis: %s", REDIS_HOST)
                await redis_client.publish(
                    "vacancy_hh",
                    json.dumps(item, ensure_ascii=False),
                )
            except Exception as e:
                print(f"Ошибка при загрузке {item.get('Сcылка')}: {e}")
                item["skills"] = []
        return result


async def main():
    page_num = 0
    URL = await db_pg.check_url(id_telegram=5103681164)
    print("url:", URL)
    async with async_playwright() as p:
        # Запускаем браузер (headless=True — без открытия окна)
        browser = await p.chromium.launch(headless=True)

        # Создаем контекст с эмуляцией реального пользователя
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )

        page = await context.new_page()

        while True:
            url = URL + f"&page={page_num}"
            content = await get_hh_page(page, url)
            if not content:
                break
            await db_pg.pool_async(content)
            page_num += 1
            await asyncio.sleep(1)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
