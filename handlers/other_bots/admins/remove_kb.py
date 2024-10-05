from aiogram import types, Router
from aiogram.filters import Command

router = Router()


@router.message(Command("remove_keyboard"))
async def remove_kb(message: types.Message):
    await message.answer(
        text="ℹ️  Нижняя клавиатура удалена!", reply_markup=types.ReplyKeyboardRemove()
    )
    await message.delete()
