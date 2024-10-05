from aiogram import types, Router, F
from aiogram.filters import Command, or_f

from data.messages import messages

router = Router()


@router.message(or_f(Command("help"), F.text == "ℹ️ Помощь"))
async def start(message: types.Message):
    await message.delete()
    await message.answer(
        messages["ru"]["help"],
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="OK", callback_data="ok_help")]
            ]
        ),
        disable_web_page_preview=True,
    )


@router.callback_query(F.data == "ok_help")
async def del_help_message(call: types.CallbackQuery):
    await call.message.delete()
