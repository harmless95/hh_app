from uuid import uuid4
from aiogram import types, Router, F
from aiogram.filters import Command

from handler_tg.handler_keyboard.keyboard_inline import (
    get_skills_keyboard,
    handler_callback_keyboard,
)
from handler_tg.handler_vacancy.handler_message import handler_message
from core.config import logger

router = Router()


@router.message(Command("search"))
async def cmd_search(message: types.Message):
    # Отправляем начальную клавиатуру (ничего не выбрано)
    await message.answer(
        "Выберите навыки для поиска:", reply_markup=get_skills_keyboard(set())
    )


@router.callback_query(F.data.startswith("toggle_"))
async def toggle_skill(callback: types.CallbackQuery):
    current_selected = await handler_callback_keyboard(callback=callback)

    # Обновляем сообщение с новой клавиатурой
    await callback.message.edit_reply_markup(
        reply_markup=get_skills_keyboard(current_selected)
    )
    await callback.answer()


@router.callback_query(F.data == "start_search")
async def process_search(callback: types.CallbackQuery):
    # Собираем финальный список
    selected = []
    for row in callback.message.reply_markup.inline_keyboard:
        for b in row:
            if b.text.startswith("+"):
                selected.append(b.text.replace("+ ", "").lower())

    if not selected:
        await callback.answer("Выберите хотя бы один навык!", show_alert=True)
        return

    logger.error("Callback info: %s", callback)
    await callback.message.edit_text(
        f"Ищу вакансии по навыкам: {', '.join(selected)}..."
    )
    logger.error("Callback info -2: %s", callback)

    id_chat = callback.message.chat.id
    user_id = callback.from_user.id
    request_id = str(uuid4())
    payload = {
        "chat": {"id": id_chat},
        "text": selected,
        "user_id": user_id,
        "request_id": request_id,
    }

    result_app = await handler_message(message_dict=payload)
    await callback.answer(result_app)
