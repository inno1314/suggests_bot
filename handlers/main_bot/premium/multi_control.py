from aiogram import Router, types, F
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from data.config import db
from data.messages import messages
from states import BotSettings
from keyboards.inline import show_bot_admins

router = Router()

@router.callback_query(BotSettings.change,
                       or_f(F.data == "multi_admins", F.data[:6] == "demote"))
async def get_admin(call: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    bot_id = int(data.get("bot_id"))
    call_data = call.data.split()

    if call_data[0] == "demote":
        admin_id = int(call_data[1])
        await db.bot_api.remove_admin(session, bot_id, admin_id)

    markup = await show_bot_admins(session, call, bot_id)
    await call.message.edit_text(text=messages['admins_list'],
                                 reply_markup=markup)

@router.callback_query(BotSettings.change, F.data[:10] == "admin_page")
async def process_admin_page(call: types.CallbackQuery, session: AsyncSession,
                             state: FSMContext):
    page = int(call.data.split()[1])
    data = await state.get_data()
    bot_id = int(data.get("bot_id"))
    markup = await show_bot_admins(session, call, bot_id, page)
    await call.message.edit_reply_markup(reply_markup=markup)

@router.callback_query(BotSettings.change, F.data == "add_admin")
async def add_admin(call: types.CallbackQuery, state: FSMContext,
                    session: AsyncSession):
    data = await state.get_data()
    bot_id = int(data.get("bot_id"))
    code = await db.codes_api.add_code(session, bot_id)
    
    deep_link = f"t.me/free_suggest_bot?start=code_{code}"
    text = f"<code>{deep_link}</code>\n\n" + messages['add_admin']

    await call.message.answer(text=text,
                         reply_markup=types.InlineKeyboardMarkup(
                         inline_keyboard=[[
                         types.InlineKeyboardButton(
                         text="OK", callback_data="OK")]]))
    await call.answer()

