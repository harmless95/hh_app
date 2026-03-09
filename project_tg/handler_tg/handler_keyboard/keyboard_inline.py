from aiogram import types
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Список доступных навыков
AVAILABLE_SKILLS = ["Python", "PostgreSQL", "Docker", "Redis", "FastAPI", "Asyncio"]


def get_skills_keyboard(selected_skills: set):
    builder = InlineKeyboardBuilder()

    for skill in AVAILABLE_SKILLS:
        # Если навык выбран, добавляем галочку
        text = f"+ {skill}" if skill in selected_skills else skill
        builder.row(
            types.InlineKeyboardButton(text=text, callback_data=f"toggle_{skill}")
        )

    builder.row(
        types.InlineKeyboardButton(text="Найти вакансии", callback_data="start_search")
    )
    return builder.as_markup()


async def handler_callback_keyboard(callback: CallbackQuery) -> set:
    # Извлекаем текущий выбор из текста кнопок (или храним в FSM/DB)
    # Для простоты примера парсим текущую клавиатуру:
    skill_to_toggle = callback.data.replace("toggle_", "")
    current_selected = set()
    for row in callback.message.reply_markup.inline_keyboard:
        for button in row:
            if button.text.startswith("+"):
                current_selected.add(button.text.replace("+ ", ""))

    # Инвертируем выбор
    if skill_to_toggle in current_selected:
        current_selected.remove(skill_to_toggle)
    else:
        current_selected.add(skill_to_toggle)
    return current_selected
