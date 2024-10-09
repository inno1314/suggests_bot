from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import db


async def banned_buttons(
    session: AsyncSession, banlist: list[int], page: int = 0
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    users_per_page = 3
    start_index = page * users_per_page
    end_index = start_index + users_per_page
    current_users = banlist[start_index:end_index]

    for sender_id in current_users:
        sender = await db.sender_api.get_sender(session, sender_id)
        builder.row(
            InlineKeyboardButton(
                text=sender.first_name, callback_data=f"unban {sender.id}"
            )
        )

    # Добавляем кнопки переключения страниц
    if start_index > 0:
        builder.row(
            InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page {page - 1}")
        )
    if end_index < len(banlist) and start_index > 0:
        builder.add(
            InlineKeyboardButton(text="Вперед ➡️", callback_data=f"page {page + 1}")
        )
    elif end_index < len(banlist):
        builder.row(
            InlineKeyboardButton(text="Вперед ➡️", callback_data=f"page {page + 1}")
        )

    builder.row(InlineKeyboardButton(text="❌", callback_data="OK"))

    return builder.as_markup()
