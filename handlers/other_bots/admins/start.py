from aiogram import types, Router
from aiogram.filters import Command

from data.config import other_bots_commands as commands
from keyboards.default import main_menu

router = Router()


@router.message(Command("start"))
async def start(message: types.Message):
    await message.delete()

    await message.bot.set_my_commands(
        commands=commands, scope=types.BotCommandScopeChat(chat_id=message.from_user.id)
    )

    await message.answer(
        f"ℹ️ Бот запущен, нижняя клавиатура загружена!", reply_markup=main_menu
    )
