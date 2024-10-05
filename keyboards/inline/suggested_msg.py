from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def make_recive_options(
    message_id: int | str, sender_id: int, sender_username: str | None = None
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🚷", callback_data=f"block {sender_id}"),
        InlineKeyboardButton(text="🧹", callback_data=f"clear {sender_id}"),
        InlineKeyboardButton(text="🗑", callback_data=f"del_msg {message_id}"),
        InlineKeyboardButton(text="📩", callback_data=f"publish {message_id}"),
    )
    if sender_username:
        builder.add(
            InlineKeyboardButton(text="👤", url=f"https://t.me/{sender_username}")
        )
    return builder.as_markup()
