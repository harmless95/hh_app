import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from core.model import help_session, HelperDB, Base
from main import app

test_helper = HelperDB(
    url="postgresql+asyncpg://postgres:postgres@localhost:5433/test_db",
    echo=False,
    echo_pool=False,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)


@pytest.fixture(scope="session")
def event_loop():
    """Создает экземпляр event loop один раз на всю сессию тестов."""

    # Мы достаем этот «заводской стандарт». В этот момент у вас еще нет нового цикла, у вас есть только инструмент для его создания.
    policy = asyncio.get_event_loop_policy()

    # Мы приказываем политике: «Создай мне совершенно новый, чистый экземпляр цикла»
    loop = policy.new_event_loop()

    # Программа "замирает" в этой точке и отдает созданный loop в пользование pytest
    yield loop

    # Выполняется только после завершения всех тестов в сессии
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    """Создаем таблицы в пустой базе перед всеми тестами"""

    # begin(): Если внутри блока async with произойдет ошибка,
    #   SQLAlchemy сама сделает rollback (откатит изменения).
    #   Если всё пройдет успешно — сделает commit (сохранит таблицы) при выходе из блока.
    async with test_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # После всех тестов можно (но не обязательно в CI) удалить таблицы
    async with test_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    """Фикстура для получения сессии в самих тестах"""

    # Мы запрашиваем у «движка» (engine) одно конкретное физическое соединение с базой.
    async with test_helper.engine.connect() as conn:

        # Открываем транзакцию на этом соединении:
        #   С этого момента база данных переходит в режим «записи в черновик».
        #   Все INSERT, UPDATE или DELETE, которые ты сделаешь,
        #   будут видны только внутри этого соединения и не сохранятся в базе окончательно, пока не будет команды commit
        async with conn.begin():

            # Создаем объект сессии SQLAlchemy и принудительно «привязываем» его к нашему открытому соединению conn:
            #  Обычно сессия сама берет соединения из пула.
            #  Но нам важно, чтобы она использовала именно то соединение, где мы только что открыли транзакцию (begin).
            session = AsyncSession(bind=conn)

            # Передаем сессию в тест.
            yield session

            # После того как тест завершился (успешно или с ошибкой), мы командуем базе: «Откатывай всё!»
            await conn.rollback()


# Фикстура запускается автоматически перед каждым тестом
@pytest_asyncio.fixture(autouse=True)
async def override_db(db_session):
    """Автоматически подменяет БД во всем приложении на время тестов"""

    # Это механизм FastAPI для подмены зависимостей (Dependency Injection)
    # Мы говорим приложению:
    #   «Когда в каком-либо роуте (эндпоинте) встретишь вызов help_session.get_session, не запускай его.
    #   Вместо этого запусти test_helper.get_session»
    app.dependency_overrides[help_session.get_session] = test_helper.get_session

    # Запускается сам тест
    yield

    # После завершения теста мы удаляем подмену из словаря dependency_overrides
    app.dependency_overrides.pop(help_session.get_session, None)


@pytest_asyncio.fixture
async def ac():
    """Асинхронный клиент для запросов"""

    # Создает экземпляр асинхронного клиента из библиотеки httpx

    # transport Это самая важная часть. Мы «скармливаем» клиенту твоё FastAPI-приложение (app) напрямую.
    #  Благодаря этому клиент не выходит в интернет и не ищет реальный сервер.
    #  Он вызывает функции твоего app напрямую в оперативной памяти.
    #  Это делает тесты мгновенными и не требует запуска сервера через uvicorn

    # base_url Устанавливает фиктивный базовый адрес
    #   Чтобы в тестах можно было писать относительные пути (например, "/login" вместо "http://test/login").
    #   Название хоста (test) не имеет значения, так как запросы идут внутрь кода
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:

        # Передает готовый клиент в тестовую функцию
        yield client
