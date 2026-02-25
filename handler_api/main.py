import httpx

url_app = "http://fastapi_app:8000/v1/data/"

# URL для поиска вакансий
url = "https://api.hh.ru/vacancies"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

# Параметры запроса
params = {
    "text": "Python разработчик",  # Ключевые слова
    # "area": 1,  # ID региона (1 - Москва)
    "per_page": 10,  # Количество результатов на странице
    "page": 0,  # Номер страницы (начинается с 0)
}


def main():
    response = httpx.get(url, params=params, headers=headers)

    result_data = []
    if response.status_code == 200:
        data = response.json()
        for item in data.get("items", []):

            current_vacancy = {
                "name_company": item.get("employer", {}).get("name"),
                "id_vacancy": item.get("id"),
                "name_vacancy": item.get("name"),
                "link": item.get("alternate_url"),
                "published_at": item.get("published_at"),
                "created_at": item.get("created_at"),
            }
            id_vac = current_vacancy["id_vacancy"]
            url_id = f"https://api.hh.ru/vacancies/{id_vac}"
            response_vac = httpx.get(url=url_id, headers=headers)
            if response_vac.status_code == 200:
                data_vac = response_vac.json()
                skills = data_vac.get("key_skills") or []
                current_vacancy["skills"] = [atr.get("name") for atr in skills]
            result_data.append(current_vacancy)

        print(result_data)
    else:
        print(f"Ошибка: {response.status_code}")

    try:
        response = httpx.post(url=url_app, json=result_data)
        response.raise_for_status()
        print(f"Успешно отправлено: {len(result_data)} вакансий")
    except httpx.HTTPStatusError as e:
        print(f"Ошибка сервера: {e.response.status_code}")
    except Exception as e:
        print(f"Ошибка подключения: {e}")


if __name__ == "__main__":
    main()
