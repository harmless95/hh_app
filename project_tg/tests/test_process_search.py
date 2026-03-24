import pytest
from unittest.mock import patch

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from handler_tg.router_inline_keyboard import process_search
from tests.conftests import mock_callback


@pytest.mark.asyncio
async def test_process_search_with_selected_skills(mock_callback):
    """Этот тест проверяет Обработчик (Хендлер)"""

    # Убедиться, что бот правильно понимает нажатую кнопку «Поиск»
    #   «Если пользователь нажал "Поиск",
    #   а на кнопках УЖЕ нарисованы плюсики,
    #   сможет ли бот прочитать их и превратить в список слов для поиска вакансий?»

    callback = mock_callback(data="start_search")

    # 1. Создаем "кукольную" клавиатуру, где один навык выбран (+), а другой нет
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="+ Python", callback_data="toggle_python")],
            [InlineKeyboardButton(text="Java", callback_data="toggle_java")],
            [InlineKeyboardButton(text="Поиск", callback_data="start_search")],
        ]
    )

    # Подкладываем эту клавиатуру в сообщение колбэка
    callback.message.reply_markup = keyboard

    # Мокаем внешний вызов API/логики вакансий
    with patch(
        "handler_tg.router_inline_keyboard.handler_message",
        return_value="Найдено 5 вакансий",
    ) as mocked_handler:

        await process_search(callback)

        # Проверяем, что в финальный список попал только "python" (в нижнем регистре без +)
        _, kwargs = mocked_handler.call_args
        assert kwargs["message_dict"]["text"] == ["python"]

        # Проверяем текст уведомления пользователю
        callback.message.edit_text.assert_called_with(
            "Ищу вакансии по навыкам: python..."
        )
