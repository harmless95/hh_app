import asyncio

from playwright.async_api import async_playwright

URL = "https://abakan.hh.ru/search/vacancy?text=playwright&salary=&ored_clusters=true&work_format=REMOTE&suggestId=5559cf1d-25a2-4c82-a36a-bdb2760ae4b0&hhtmFrom=vacancy_search_list&hhtmFromLabel=vacancy_search_line"

async def get_hh_page():
    async with async_playwright() as p:
        # Запускаем браузер (headless=True — без открытия окна)
        browser = await p.chromium.launch(headless=True)

        # Создаем контекст с эмуляцией реального пользователя
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )

        page = await context.new_page()

        # Переходим по ссылке
        await page.goto(URL, wait_until="networkidle")

        # Можно сделать скриншот, чтобы проверить, не вылезла ли капча
        await page.screenshot(path="./resource/hh_check.png")

        # Получаем HTML всей страницы
        content = await page.content()

        vacancy = await page.locator('div[data-qa="vacancy-serp__vacancy"]').all()
        result = []

        for card in vacancy:
            titles = await card.locator('[data-qa="serp-item__title-text"]').text_content()
            company_name = await card.locator('[data-qa="vacancy-serp__vacancy-employer"]').text_content()
            link_vacancy = await card.locator('[data-qa="serp-item__title"]').get_attribute("href")

            result.append(
                {
                    "Название вакансии": titles,
                    "Название компании": company_name,
                    "Сыллка на вакансию": link_vacancy,
                }
            )
        with open("./resource/vacancy_file.txt", "w", encoding="utf-8") as file:
            for idx, item in enumerate(result):
                print(f"Загруженна вакансия: {idx + 1}")
                await page.goto(item.get("Сыллка на вакансию"), wait_until="domcontentloaded")
                item["skills"] = await page.locator('[data-qa="skills-element"]').all_text_contents()
                file.write(str(item) + "\n")
                print(item)

        await browser.close()
        return content

if __name__ == "__main__":
    asyncio.run(get_hh_page())