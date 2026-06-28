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
    text = "<blockquote><b>⚙️ Настройки бота</b></blockquote>\n\n"
    text += f"<b>Бот: <i>{html.link(bot.name, bot.url)}</i></b>\n\n"
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



@router.callback_query(BotSettings.change, F.data == "bot_stats")
async def bot_stats(
    call: types.CallbackQuery, session: AsyncSession, state: FSMContext
):
    from utils import generate_bot_suggestions_chart, chart_cache
    data = await state.get_data()
    bot_id = int(data.get("bot_id"))
    
    cache_key = f"bot_stats:{bot_id}"
    cached_data = chart_cache.get(cache_key)
    
    if cached_data:
        photo, caption = cached_data
    else:
        bot = await db.bot_api.get_bot(session, bot_id)
        
        total_suggestions = await db.message_api.get_bot_suggestions_count(session, bot_id)
        unique_senders = await db.message_api.get_bot_unique_senders_count(session, bot_id)
        channels = await db.channel_api.get_channels_info(session, bot_id)
        banned_users = len(bot.banlist) if bot.banlist else 0
        
        chart_path = await generate_bot_suggestions_chart(session, bot_id)
        photo = types.FSInputFile(chart_path)
        
        caption = (
            f"<b>📊 Статистика бота <i>{html.link(bot.name, bot.url)}</i></b>\n\n"
            f"📩 Всего предложений: <code>{total_suggestions}</code>\n"
            f"👤 Уникальных отправителей: <code>{unique_senders}</code>\n"
            f"📢 Подключено каналов: <code>{len(channels)}</code>\n"
            f"🚫 Заблокировано пользователей: <code>{banned_users}</code>"
        )
    
    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="🔙 Назад", callback_data=f"back_to_settings:{bot_id}"
                )
            ]
        ]
    )
    
    await call.message.delete()
    sent_msg = await call.message.answer_photo(photo=photo, caption=caption, reply_markup=markup)
    if not cached_data and sent_msg and sent_msg.photo:
        chart_cache.set(cache_key, (sent_msg.photo[-1].file_id, caption))

@router.callback_query(F.data.startswith("back_to_settings:"))
async def back_to_settings(
    call: types.CallbackQuery, session: AsyncSession, state: FSMContext
):
    bot_id = int(call.data.split(":")[1])
    await call.message.delete()
    
    await state.set_state(BotSettings.change)
    await state.update_data(bot_id=bot_id)
    
    bot = await db.bot_api.get_bot(session, bot_id)
    text = "<blockquote><b>⚙️ Настройки бота</b></blockquote>\n\n"
    text += f"<b>Бот: <i>{html.link(bot.name, bot.url)}</i></b>\n\n"
    text += messages["bot_settings"]
    markup = await setts_buttons(session, bot_id)
    await call.message.answer(text=text, reply_markup=markup)