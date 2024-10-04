from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

async def make_formatting_markup(bot_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👋 Стартовое",
                                 callback_data="start_msg_formatting")
        ],
        [
            InlineKeyboardButton(text="✍️ Ответное",
                                 callback_data="answer_msg_formatting")
        ],
        [
            InlineKeyboardButton(text="📎 Дополнительное",
                                 callback_data="post_formatting")
        ],
        [
            InlineKeyboardButton(text="🔙",
                                 callback_data=f"setts {bot_id}")
        ]
    ])

