import logging

from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import db
from states import GiveSub

logger = logging.getLogger(__name__)

router = Router()


sub_types = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="30 дней (159₽)",
                             callback_data="month"),
        InlineKeyboardButton(text="90 дней (429₽)",
                             callback_data="three_months")
    ],
    [
        InlineKeyboardButton(text="180 дней (799₽)",
                             callback_data="half_year"),
        InlineKeyboardButton(text="365 дней (1299₽)",
                             callback_data="year")
    ],
    [
        InlineKeyboardButton(text="Отменить подписку",
                             callback_data="clear_sub")
    ],
    [
        InlineKeyboardButton(text="Назад",
                             callback_data="to_admins_menu")
    ]
])


@router.callback_query(F.data == "give_sub_to_user")
async def give_sub_to_user(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(GiveSub.choosing_option)
    await call.answer()
    await call.message.answer(text="<b>Выбери опцию:</b>",
                              reply_markup=sub_types)

@router.callback_query(GiveSub.choosing_option,
                       F.data.in_(["month", "three_months", "half_year", "year", "clear_sub"]))
async def get_id_for_sub(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(plan=call.data)
    await call.message.edit_text("<b>Введи ID пользователя:</b>")
    await state.set_state(GiveSub.getting_id)

@router.message(GiveSub.getting_id, F.text)
async def give_sub_to_user_id(message: types.Message, state: FSMContext,
                              session: AsyncSession):
    state_data = await state.get_data()
    plan = str(state_data.get("plan"))

    user_id = message.text
    if user_id is None or not user_id.isnumeric():
        return await message.answer("Некорректный ввод")
    else:
        admin_id = int(user_id)

    admin = await db.admin_api.get_admin(session, admin_id)
    if admin is None:
        return await message.answer("Пользователь не найден")

    if plan == "clear_sub":
        await db.subscription_api.clean_subscriptions(session, admin_id)
        return await message.answer("Подписка обнулена")

    await db.subscription_api.add_subscription(session, admin_id,
                                               subscription_type=plan)
    bots = await db.admin_api.get_admins_bots(session, admin_id)
    for bot in bots:
        await db.bot_api.update_bot_field(session, bot.id, "is_premium", True)
        logger.info(f"Status is_premium was updated for bot {bot.id}")
    await message.answer("Изменения применены")
    await state.clear()

