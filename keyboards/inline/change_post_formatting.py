from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def formatting_markup(field: str, bot_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Вернуть значение по умолчанию",
                    callback_data=f"clear_{field}",
                )
            ],
            [InlineKeyboardButton(text="🔙", callback_data=f"setts {bot_id}")],
        ]
    )
