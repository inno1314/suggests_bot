from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ok_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="OK",
                              callback_data="OK")]
    ]
)
