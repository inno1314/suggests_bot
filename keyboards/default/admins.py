from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="🧹 Очистить предложку")
    ],
    [
        KeyboardButton(text="ℹ️ Помощь"),
        KeyboardButton(text="🚷 Banlist")
    ]
], resize_keyboard=True)
