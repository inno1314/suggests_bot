from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import db
from states import BotSettings
from keyboards.inline import formatting_markup
from data.messages import messages

router = Router()

@router.callback_query(BotSettings.change, F.data == "post_formatting")
async def post_formatting(call: types.CallbackQuery, state: FSMContext,
                          session: AsyncSession):
    data = await state.get_data()
    bot_id = int(data.get("bot_id"))
    db_bot = await db.bot_api.get_bot(session, bot_id)
    current_formatting = db_bot.post_formatting if db_bot.post_formatting is not None \
        else "<i>Не установлена</i>"
    text = messages['ru']['change_formatting'] + current_formatting

    await state.set_state(BotSettings.formatting)
    await state.update_data(message_id=call.message.message_id)

    markup = await formatting_markup(bot_id)
    await call.message.edit_text(text, reply_markup=markup)

@router.callback_query(BotSettings.formatting, F.data == "no_formatting")
async def delete_formatting(call: types.CallbackQuery, state: FSMContext,
                            session: AsyncSession):
    data = await state.get_data()
    bot_id = int(data.get("bot_id"))

    await db.bot_api.update_bot_field(session, bot_id,
                                      "post_formatting", None)
    text = messages['ru']['change_formatting'] + "<i>Не установлена</i>"
    
    markup = await formatting_markup(bot_id)
    await call.message.edit_text(text, reply_markup=markup)

@router.message(BotSettings.formatting, F.text)
async def set_new_formatting(message: types.Message, state: FSMContext,
                             session: AsyncSession):
    bot = message.bot
    new_formatting = message.html_text
    data = await state.get_data()
    bot_id = int(data.get("bot_id"))
    
    await message.delete()
    await db.bot_api.update_bot_field(session, bot_id,
                                      "post_formatting", new_formatting)
    
    data = await state.get_data()
    message_id = int(data.get("message_id"))
    text = messages['ru']['change_formatting'] + new_formatting
    markup = await formatting_markup(bot_id)
    await bot.edit_message_text(text, message.from_user.id,
                                message_id, reply_markup=markup)

@router.message(BotSettings.formatting)
async def set_new_formatting(message: types.Message):
    await message.delete()

