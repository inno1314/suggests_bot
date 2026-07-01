from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

payment_methods = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Написать в Telegram 💬",
                url="https://t.me/inno_1314",
            )
        ],
        [
            InlineKeyboardButton(
                text="Назад 🔙",
                callback_data="to_sub_plans",
            )
        ],
    ]
)
