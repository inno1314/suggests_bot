from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

payment_methods = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="🟣 YooMoney — Карта РФ",
                             callback_data="yoomoney")
    ],
    [
        InlineKeyboardButton(text="🟡 AAIO —  СБП / UA Карта",
                             callback_data="aaio")
    ],
    [
        InlineKeyboardButton(text="🔵 CryptoBot — Крипта",
                             callback_data="crypto_bot")
    ],
    [
        InlineKeyboardButton(text="🔙",
                             callback_data="to_sub_plans")
    ]
])
