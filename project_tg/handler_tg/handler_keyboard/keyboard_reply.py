from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

router_reply = Router()


@router_reply.message(Command("help"))
async def builder_reply(message: Message):
    builder = ReplyKeyboardBuilder()
    builder.button(text="/search")
    builder.adjust(1)
    markup = builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
    await message.answer(text="Выдвижные кнопки", reply_markup=markup)
