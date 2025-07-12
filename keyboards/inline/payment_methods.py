from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

payment_methods = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🟣 Plat — Карта RU", callback_data="plat_card")],
        [
            InlineKeyboardButton(
                text="⚫️ Plat — Система быстрых платежей",
                callback_data="plat_sbp",
            )
        ],
        [InlineKeyboardButton(text="🟡 AAIO —  СБП / Карта UA", callback_data="aaio")],
        [InlineKeyboardButton(text="🔵 CryptoBot — Крипта", callback_data="cryptobot")],
        [InlineKeyboardButton(text="🔙", callback_data="to_sub_plans")],
    ]
)
