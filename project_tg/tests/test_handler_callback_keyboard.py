import pytest
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from handler_tg.handler_keyboard.keyboard_inline import handler_callback_keyboard
from tests.conftests import mock_callback


@pytest.mark.asyncio
async def test_handler_callback_toggle_on(mock_callback):
    # Ситуация: Нажата кнопка Redis, в сообщении пока ничего не выбрано
    callback = mock_callback(data="toggle_Redis")
    callback.message.reply_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Redis", callback_data="toggle_Redis")],
            [InlineKeyboardButton(text="Python", callback_data="toggle_Python")],
        ]
    )

    # Вызываем функцию
    result = await handler_callback_keyboard(callback)

    # Должен вернуться сет с Redis
    assert result == {"Redis"}


@pytest.mark.asyncio
async def test_handler_callback_toggle_off(mock_callback):
    # Ситуация: Нажата кнопка Python, но она УЖЕ была выбрана (с плюсиком)
    callback = mock_callback(data="toggle_Python")
    callback.message.reply_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="+ Python", callback_data="toggle_Python")],
            [InlineKeyboardButton(text="Redis", callback_data="toggle_Redis")],
        ]
    )

    # Вызываем функцию
    result = await handler_callback_keyboard(callback)

    # Сет должен быть пустым (сняли выделение)
    assert result == set()
