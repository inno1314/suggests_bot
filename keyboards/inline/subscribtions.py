from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

sub_types = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="30 дней (159₽)", callback_data="month"),
            InlineKeyboardButton(text="90 дней (429₽)", callback_data="three_months"),
        ],
        [
            InlineKeyboardButton(text="180 дней (799₽)", callback_data="half_year"),
            InlineKeyboardButton(text="365 дней (1299₽)", callback_data="year"),
        ],
        [InlineKeyboardButton(text="Назад", callback_data="to_menu")],
    ]
)

admin_sub_types = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="30 дней (159₽)", callback_data="month"),
            InlineKeyboardButton(text="90 дней (429₽)", callback_data="three_months"),
        ],
        [
            InlineKeyboardButton(text="180 дней (799₽)", callback_data="half_year"),
            InlineKeyboardButton(text="365 дней (1299₽)", callback_data="year"),
        ],
        [InlineKeyboardButton(text="Отменить подписку", callback_data="clear_sub")],
        [InlineKeyboardButton(text="Назад", callback_data="to_admins_menu")],
    ]
)
