from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline import main_admins_markup
from data.config import db
from data.messages import messages

router = Router()


@router.message(Command("admin"))
async def show_menu(message: types.Message):
    await message.delete()
    await message.answer(
        text=messages["admin_panel"], reply_markup=main_admins_markup
    )


@router.callback_query(F.data == "to_admins_menu")
async def to_menu_from_call(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.delete()
    await call.message.answer(
        text=messages["admin_panel"], reply_markup=main_admins_markup
    )


# @router.message(Command("ad_to_db"))
# async def debug(message: types.Message, session: AsyncSession):
#     model = message.model_dump_json()
#     json_model = json.loads(model)
#
#     await db.ads_api.add_ad_message(session=session,
#                                     html_text="Спасибо за ваше сообщение!",
#                                     data=json_model)
#
#     await message.delete()
