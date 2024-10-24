from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

payment_methods = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🟣 YooMoney — Карта РФ", callback_data="yoomoney")],
        [InlineKeyboardButton(text="🟢 NicePay — СБП / Tinkoff", callback_data="nicepay")],
        [InlineKeyboardButton(text="🟡 AAIO —  СБП / UA Карта", callback_data="aaio")],
        [
            InlineKeyboardButton(
                text="🔵 CryptoBot — Крипта", callback_data="cryptobot"
            )
        ],
        [InlineKeyboardButton(text="🔙", callback_data="to_sub_plans")],
    ]
)
