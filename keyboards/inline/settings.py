from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import db

async def setts_buttons(session: AsyncSession, bot_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    bot = await db.bot_api.get_bot(session, bot_id)
    sign = bool(bot.sign_messages)
    status_emoji = "🟢" if sign else "🔴"
    builder.row(InlineKeyboardButton(text=status_emoji + " Подписи в постах",
                                     callback_data="change_sign_setts"))
    builder.row(InlineKeyboardButton(text="👥 Совместное управление",
                                     callback_data="multi_admins"))
    builder.row(InlineKeyboardButton(text="💼 Оформление",
                                     callback_data="formats"))
    builder.row(InlineKeyboardButton(text="🔙",
                                     callback_data="to_botlist"))
    return builder.as_markup()

