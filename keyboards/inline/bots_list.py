from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.model import Bot


async def bots_list(bots: list[Bot], page: int = 0) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if len(bots) <= 10:
        builder.row(
            InlineKeyboardButton(
                text="🤖 ДОБАВИТЬ НОВОГО БОТА", callback_data="create_bot"
            )
        )

    bots_per_page = 2
    start_index = page * bots_per_page
    end_index = start_index + bots_per_page
    current_bots = bots[start_index:end_index]

    for bot in current_bots:
        status = bool(bot.is_active)
        work_status_emoji = "🟢" if status else "🔴"
        action_emoji = "⏸" if status else "▶️"
        builder.row(
            InlineKeyboardButton(
                text=work_status_emoji + str(bot.name), url=str(bot.url)
            )
        )

        builder.row(
            InlineKeyboardButton(text="❌", callback_data=f"del {bot.id}"),
            InlineKeyboardButton(text=action_emoji, callback_data=f"switch {bot.id}"),
            InlineKeyboardButton(text="⚙️", callback_data=f"setts {bot.id}"),
        )

    if start_index > 0 and end_index < len(bots):
        builder.row(
            InlineKeyboardButton(text="⬅️ Назад", callback_data=f"bots_page {page - 1}"),
            InlineKeyboardButton(
                text="Вперед ➡️", callback_data=f"bots_page {page + 1}"
            ),
        )
    elif start_index == 0 and end_index < len(bots):
        builder.row(
            InlineKeyboardButton(text="Вперед ➡️", callback_data=f"bots_page {page + 1}")
        )
    elif start_index > 0 and end_index >= len(bots):
        builder.row(
            InlineKeyboardButton(text="⬅️ Назад", callback_data=f"bots_page {page - 1}")
        )

    builder.row(InlineKeyboardButton(text="🔙", callback_data="to_menu"))

    return builder.as_markup(resize_keyboard=True)
