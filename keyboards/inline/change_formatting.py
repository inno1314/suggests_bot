from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

async def formatting_markup(bot_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
        [
            InlineKeyboardButton(text="❌ Удалить подпись",
                                       callback_data="no_formatting")
        ],
        [
            InlineKeyboardButton(text="🔙",
                                       callback_data=f"setts {bot_id}")
        ]
    ]
)
