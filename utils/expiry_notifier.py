import logging
from datetime import datetime, timezone
from aiogram import Bot, types

from utils import clean_subscription
from data.messages import messages


logger = logging.getLogger(__name__)

async def db_subscriptions_checker(bot: Bot, db):
    logger.info("APS started subscriptions checking job...")
    async with db.session as session:
        subscriptions = await db.subscription_api.get_all_subscriptions(session)

    for sub in subscriptions:
        days_left = (sub.end_date - datetime.now(timezone.utc)).days
        if 0 <= days_left <= 3:
            text = f"<b>⚠️До истечения подписки осталось {days_left} дней!</b>\n\n"
            text += messages['ru']['expiring_sub']
            await bot.send_message(chat_id=sub.admin_id, text=text,
                                   reply_markup=types.InlineKeyboardMarkup(
                                   inline_keyboard=[
                                   [
                                   types.InlineKeyboardButton(text="❌",
                                                              callback_data="OK")
                                   ]]))
            logger.info(f"User {sub.admin_id} was notified about expiration")
        if days_left < 0:
            await clean_subscription(session, sub.admin_id, db)

    logger.info("APS completed subscriptions checking job")

