from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import db

async def show_bot_admins(session: AsyncSession,
                          call: CallbackQuery,
                          bot_id: int,
                          page: int = 0) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    list_of_admins = await db.bot_api.get_bots_admins(session, bot_id)
    admins_per_page = 3
    start_index = page * admins_per_page
    end_index = start_index + admins_per_page
    current_admins = list_of_admins[start_index:end_index]

    for admin_id in current_admins:
        admin = await db.admin_api.get_admin(session, admin_id)
        if admin.id == call.from_user.id:
            builder.row(InlineKeyboardButton(text=call.from_user.full_name,
                                     url=call.from_user.url))
            continue
        builder.row(InlineKeyboardButton(text=admin.name,
                                         callback_data=f"demote {admin_id}"))
    
    if start_index > 0 and end_index < len(list_of_admins):
        builder.row(
            InlineKeyboardButton(text="⬅️ Назад", callback_data=f"admin_page {page - 1}"),
            InlineKeyboardButton(text="Вперед ➡️", callback_data=f"admin_page {page + 1}")
        )
    elif start_index == 0 and end_index < len(list_of_admins):
        builder.row(InlineKeyboardButton(text="Вперед ➡️",
                                         callback_data=f"admin_page {page + 1}"))
    elif start_index > 0 and end_index >= len(list_of_admins):
        builder.row(InlineKeyboardButton(text="⬅️ Назад",
                                         callback_data=f"admin_page {page - 1}"))

    builder.row(InlineKeyboardButton(text="Добавить администратора",
                                     callback_data="add_admin"))
    builder.row(InlineKeyboardButton(text="🔙", callback_data=f"setts {bot_id}"))
    return builder.as_markup()
