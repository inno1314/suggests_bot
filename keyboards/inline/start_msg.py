from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

start_msg_markup = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="🤖 Ваши боты",
                             callback_data="view_bots")
    ],
    [
        InlineKeyboardButton(text="👨‍💻 Поддержка",
                             url="https://t.me/rt_coder")
        # InlineKeyboardButton(text="Язык",
        #                      callback_data="change_language")
    ],
    [
        InlineKeyboardButton(text="🪄 Приобрести подписку",
                             callback_data="get_premium")
    ]
])

