import pytest
from unittest.mock import AsyncMock
from aiogram import Bot
from aiogram.types import User, Chat, Message


@pytest.fixture
def mock_bot():
    """mock_bot позволяет «обмануть» программу, подсунув ей имитацию бота"""

    # spec=Bot: Это «чертеж» или «инструкция».
    #   Мы говорим: «Этот объект должен вести себя строго как класс Bot из библиотеки aiogram»
    return AsyncMock(spec=Bot)


@pytest.fixture
def mock_message():
    def _create_message(text="/start"):

        # Здесь мы создаем реальные объекты aiogram
        #   Это нужно, потому что в хендлере используется message.from_user.full_name.
        #   Если мы подсунем туда просто текст, код упадет.
        user = User(id=1, is_bot=False, first_name="Vitaliy", last_name="")
        chat = Chat(id=1, type="private")

        # Имитирует Message если у него несуществующий метод (например, message.send_pizza()), тест сразу выдаст ошибку
        message = AsyncMock(spec=Message)

        # Мы "вручную" наполняем наш поддельный объект данными, которые ожидает хендлер.
        # Теперь, когда хендлер обратится к message.from_user.first_name, он получит "Vitaliy"
        message.text = text
        message.from_user = user
        message.chat = chat

        # В реальной жизни .answer() отправляет запрос на сервера Telegram.
        #   В тесте нам это запрещено (нет интернета/токена)
        #   Мы заменяем реальный метод на "ловушку" AsyncMock
        #   Теперь, когда хендлер напишет await message.answer("Привет"),
        #   ничего никуда не отправится, но AsyncMock запомнит, что его вызывали именно с текстом "Привет"

        message.answer = AsyncMock()
        return message

    return _create_message


from aiogram.types import CallbackQuery


@pytest.fixture
def mock_callback():
    def _create_callback(data="some_data"):
        user = User(id=1, is_bot=False, first_name="Vitaliy")
        # CallbackQuery требует объект Message, на котором висела кнопка
        message = AsyncMock(spec=Message)

        message.edit_text = AsyncMock()
        message.edit_reply_markup = AsyncMock()
        message.answer = AsyncMock()

        chat = Chat(id=12345, type="private")

        callback = AsyncMock(spec=CallbackQuery)
        callback.from_user = user
        callback.message = message
        callback.data = data
        message.chat = chat
        callback.answer = AsyncMock()
        return callback

    return _create_callback
