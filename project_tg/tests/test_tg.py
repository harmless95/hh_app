import pytest
from aiogram.fsm.context import FSMContext
from unittest.mock import AsyncMock

from main import command_start, command_stop
from tests.conftests import mock_message, mock_bot


@pytest.mark.asyncio
async def test_get_start_command(mock_message):
    # Создаем виртуальное сообщение
    message = mock_message(text="/start")

    # Вызываем твой хендлер
    await command_start(message)

    # Проверяем результат
    expected_text = f"Привет, <b>{message.from_user.full_name}</b>! Укажите по каким навыкам искать?"

    # Проверяем, что метод answer был вызван с правильным текстом
    message.answer.assert_called_once()
    args, kwargs = message.answer.call_args
    assert args[0] == expected_text
    assert kwargs["parse_mode"] == "HTML"


async def test_stop_command(mock_message):
    message = mock_message(text="/stop")

    # Это создает объект, который ведет себя как настоящий контекст состояний
    state = AsyncMock(spec=FSMContext)

    await command_stop(message, state)

    expected_text = "Все процессы остановились"

    message.answer.assert_called_once()
    args, _ = message.answer.call_args
    assert args[0] == expected_text
