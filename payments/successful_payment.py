import logging
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import db
from data.messages import messages


logger = logging.getLogger(__name__)

async def successful_payment(session: AsyncSession,
                             admin_id: int,
                             message: types.Message,
                             plan: str):
    """
    Обрабатывает успешный платеж
    :param call: types.CallbackQuery
    :param payment_amount: сумма платежа
    :return:
    """
    await db.subscription_api.add_subscription(session, admin_id,
                                               subscription_type=plan)
    bots = await db.admin_api.get_admins_bots(session, admin_id)
    for bot in bots:
        await db.bot_api.update_bot_field(session, bot.id, "is_premium", True)
        logger.info(f"Status is_premium was updated for bot {bot.id}")
    await message.edit_text(text=messages['successful_payment'],
                           reply_markup=types.InlineKeyboardMarkup(
                           inline_keyboard=[[types.InlineKeyboardButton(text="🔙",
                                                      callback_data="to_sub_plans")
                                             ]]))

