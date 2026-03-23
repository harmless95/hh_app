import pytest

import api.routers as routers_module


@pytest.fixture
def patch_taskiq(mocker, db_session):
    """
    Универсальный помощник для запуска задач TaskIQ прямо в тесте.
    """

    def _patch(task_object):
        async def _mock_kiq_logic(body, **_):
            # Мы вызываем саму функцию задачи,
            # автоматически подставляя нашу тестовую сессию
            return await task_object(body, session=db_session)

        # Находим все места, где эта задача может быть импортирована,
        # и подменяем её метод .kiq
        mocker.patch.object(task_object, "kiq", side_effect=_mock_kiq_logic)

        # Если задача импортирована в роутеры как отдельный объект,
        # патчим её и там (для надежности)
        if hasattr(routers_module, task_object.__name__):
            target = getattr(routers_module, task_object.__name__)
            mocker.patch.object(target, "kiq", side_effect=_mock_kiq_logic)

    return _patch
