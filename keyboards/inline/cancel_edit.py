from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

cancel_edit_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_edit")]
    ]
)
