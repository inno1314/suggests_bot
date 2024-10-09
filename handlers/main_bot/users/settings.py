from aiogram import html, types, F, Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from data.messages import messages
from data.config import db
from utils import is_main_admin
from keyboards.inline import setts_buttons
from states import BotSettings

router = Router()


@router.callback_query(F.data[:5] == "setts")
async def bot_settings(
    call: types.CallbackQuery, session: AsyncSession, state: FSMContext
):
    bot_id = int(call.data.split()[1])

    if not await is_main_admin(call, session, db, bot_id):
        return

    await state.set_state(BotSettings.change)
    await state.update_data(bot_id=bot_id)

    bot = await db.bot_api.get_bot(session, bot_id)
    text = "<b>Настройки бота</b>\n\n"
    text += f"Бот: <i><b>{html.link(bot.name, bot.url)}</b></i>\n\n"
    text += messages["bot_settings"]
    markup = await setts_buttons(session, bot_id)
    await call.message.edit_text(text=text, reply_markup=markup)


@router.callback_query(BotSettings.change, F.data == "change_sign_setts")
async def change_sign_setts(
    call: types.CallbackQuery, session: AsyncSession, state: FSMContext
):
    data = await state.get_data()
    bot_id = int(data.get("bot_id"))
    bot = await db.bot_api.get_bot(session, bot_id)
    sign = False if bot.sign_messages else True
    await db.bot_api.update_bot_field(
        session, bot_id, field_name="sign_messages", new_value=sign
    )
    markup = await setts_buttons(session, bot_id)
    await call.message.edit_reply_markup(reply_markup=markup)
