import asyncio
import os
import logging
import httpx

import redis.asyncio as redis

from playwright.async_api import async_playwright

logger = logging.getLogger("ParseData")


URL = f"https://hh.ru/search/vacancy?text=python&items_on_page=20"
url_app = "http://fastapi_app:8000/v1/data/"


REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=6379,
    decode_responses=True,
)
name_channel = "list_id_vacancy"
name_channel_duble = "duble_vacancy"


async def get_hh_page(page, url):
    data_list = await redis_client.smembers(name_channel)
    data_duble = await redis_client.smembers(name_channel_duble)

    # Переходим по ссылке
    await page.goto(url, wait_until="domcontentloaded")

    await asyncio.sleep(2)

    # Можно сделать скриншот, чтобы проверить, не вылезла ли капча
    await page.screenshot(path="./resource/hh_check.png")

    # Получаем HTML всей страницы
    content = await page.content()

    # Проверяем на наличие вакансий
    vacancy = await page.locator('div[data-qa="vacancy-serp__vacancy"]').all()
    logger.info("Найдено %s вакансий", len(vacancy))
    print("кол-во вакнсий", len(vacancy))
    list_vacancy = []
    list_id_vacancy = []
    list_duble_vacancy = []

    for card in vacancy:
        id_vac = await card.locator(
            'div[class="vacancy-card--n77Dj8TY8VIUF0yM font-inter"]'
        ).get_attribute("id")
        if not id_vac or id_vac in data_list:
            continue

        tit = card.locator('[data-qa="serp-item__title-text"]')
        if await tit.count() > 0:
            titles = await tit.text_content()
        else:
            titles = "Название вакансии не указанно"

        comp_name = card.locator('[data-qa="vacancy-serp__vacancy-employer"]')
        if await comp_name.count() > 0:
            company_name = await comp_name.text_content()
        else:
            company_name = "Название компании не указанно"
        duble_vac = f"{titles}|{company_name}"
        if duble_vac in data_duble or duble_vac in list_duble_vacancy:
            continue
        list_duble_vacancy.append(duble_vac)

        link_vacancy = await card.locator('[data-qa="serp-item__title"]').get_attribute(
            "href"
        )

        list_vacancy.append(
            {
                "id_vacancy": int(id_vac),
                "name_vacancy": titles,
                "name_company": company_name,
                "link": link_vacancy,
            }
        )
        list_id_vacancy.append(id_vac)

    if list_id_vacancy:
        await redis_client.sadd(
            name_channel,
            *list_id_vacancy,
        )
    if list_duble_vacancy:
        await redis_client.sadd(name_channel_duble, *list_duble_vacancy)
    return list_vacancy


async def get_link(page, list_vacancy: list):
    for idx, item in enumerate(list_vacancy):
        try:
            logger.info("Загруженна вакансия: %s", (idx + 1))
            print("загружен", idx)
            await page.goto(
                item.get("link"),
                wait_until="domcontentloaded",
                timeout=15000,
            )
            item["skills"] = await page.locator(
                '[data-qa="skills-element"]'
            ).all_text_contents()
        except Exception as e:
            print(f"Ошибка при загрузке {item.get('link')}: {e}")
            item["skills"] = []
    return list_vacancy


async def main():
    page_num = 0
    list_content = []
    async with async_playwright() as p:
        # Запускаем браузер (headless=True — без открытия окна)
        browser = await p.chromium.launch(headless=True)

        # Создаем контекст с эмуляцией реального пользователя
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )

        page = await context.new_page()

        while page_num < 3:
            url = URL + f"&page={page_num}&order_by=publication_time"
            content = await get_hh_page(page, url)
            if not content:
                break
            list_content.extend(content)
            page_num += 1
            await asyncio.sleep(1)
        list_data = await get_link(page=page, list_vacancy=list_content)

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url=url_app, json=list_data)
                response.raise_for_status()
                print(f"Успешно отправлено: {len(list_data)} вакансий")
            except httpx.HTTPStatusError as e:
                print(f"Ошибка сервера: {e.response.status_code}")
            except Exception as e:
                print(f"Ошибка подключения: {e}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
