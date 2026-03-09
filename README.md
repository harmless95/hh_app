# Telegram vacancy Bot

Асинхронный сервис для поиска вакансий по способностям.

## Архитектура системы

- **FastAPI**: Принимает Webhook от Telegram, выполняет первичную валидацию и делегирует обработку в фон.
- **SQLAlchemy (Async)**: Асинхронная запись в **PostgreSQL**.
- **Redis Pub/Sub**: Шина событий. После записи в БД улетает сигнал для мгновенного уведомления.
- **Aiogram Listener**: Слушает Redis-канал и отправляет пользователю результат обработки.
- **Aiogram keyboard**: Обрабатывает выбранные вакансии для поиска по полному соответствию.

## Стек технологий

* **Python 3.10+** | **FastAPI** | **Aiogram 3.x**
* **PostgreSQL** (БД) | **SQLAlchemy + Alembic** (ORM & Миграции)
* **Redis** (Pub/Sub брокер)
* **Pydantic v2** (Валидация схем)
* **Httpx** (Асинхронные запросы)


## Установка и запуск

1. Клонирование
```
git clone https://github.com/harmless95/hh_app
cd hh_app
```
Используйте код с осторожностью.

2. Настройка окружения (.env)
В корне проекта или в соответствующих папках сервисов:
env
```
# --- PostgreSQL (Docker) ---
- POSTGRES_USER=user
- POSTGRES_PASSWORD=password
- POSTGRES_DB=db
```
```
# --- APP Service ---
# Redis
APP_CONFIG__REDIS__URL=redis://redis:6379/0
APP_CONFIG__REDIS__CHANNEL=channel

# Database
APP_CONFIG__DB__URL=postgresql+asyncpg://user:password@localhost:5432/db_name
```
```
# --- project_tg Service ---
#TELEGRAM
APP_CONFIG__CONFIG_TG__TOKEN=token
APP_CONFIG__CONFIG_TG__PORT=8000

#redis
APP_CONFIG__REDIS__URL=redis://redis:6379/0
APP_CONFIG__REDIS__CHANNEL=channel

# URL FastAPI
APP_CONFIG__APP_DB__URL=app
```
Используйте код с осторожностью.

3. Запуск через Docker (рекомендуется)

```
docker-compose up --build
```
Используйте код с осторожностью.


## API Endpoints
* Метод	Эндпоинт	Описание
* POST	/v1/data/	Сохраненние данных в Базе данных
* POST	/v1/data/tg/	Получаем список способностей и при полном соотвествии отправляем

### Жизненный цикл сообщения
- User: Пишет в боте /search.
- User: Выводится список способностей отмечаем по каким искать и нажимаем "Найти вакансию".
- FastAPI: Получает Webhook. Получает список и отправлает в очередь Taskiq и возвращает подтверждение получения.
- Bot: Что бы пользователь не ждал уведомляет, что сообщение обрабатывается.
- Taskiq: Брокер фоне берет данные из очереди и обращается к базе данных для поиска по соответствию и отправляет в redis.
- Redis: Публикует в определенный канал
- Bot: Получает сигнал из Redis и присылает юзеру: "Данные вакансий".