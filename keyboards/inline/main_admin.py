from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_admins_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Аналитика", callback_data="show_incomes")],
        [InlineKeyboardButton(text="Рассылка", callback_data="mailing")],
        [InlineKeyboardButton(text="Рекламное сообщение", callback_data="edit_ads")],
        [
            InlineKeyboardButton(
                text="Выдать подписку", callback_data="give_sub_to_user"
            )
        ],
    ]
)

back_markup = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="🔙", callback_data="to_admins_menu")]]
)
