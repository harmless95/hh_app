import httpx

from core.config import logger, setting

url_app = setting.app_db.url


async def handler_message(message_dict: dict):

    logger.error("Data TG: %s, %s", type(message_dict), message_dict)
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url=url_app, json=message_dict)
            logger.error("Resp: %s", response)
            if response.status_code == 200:
                return "Сообщение обработанно"

            logger.warning("API Error %s: %s", response.status_code, response.text)
            return "Не удалось обработать данные"

    except httpx.ReadTimeout:
        return "Сервер слишком долго думал, но мы продолжаем обработку"
    except Exception as ex:
        logger.exception("Webhook sending failed")
        return "Ошибка связи с сервером"
