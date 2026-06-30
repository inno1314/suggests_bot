import logging
from datetime import datetime, timezone
from aiogram import Bot, types
from aiogram.exceptions import TelegramForbiddenError

from utils import clean_subscription
from data.messages import messages


logger = logging.getLogger(__name__)


async def db_subscriptions_checker(bot: Bot, db):
    logger.info("APS started subscriptions checking job...")
    async with db.session as session:
        subscriptions = await db.subscription_api.get_all_subscriptions(session)

    for sub in subscriptions:
        try:
            days_left = (sub.end_date - datetime.now(timezone.utc)).days
            if 0 <= days_left <= 3:
                text = f"<b>⚠️ До истечения подписки осталось {days_left} дня!</b>\n\n"
                text += messages["expiring_sub"]
                await bot.send_message(
                    chat_id=sub.admin_id,
                    text=text,
                    reply_markup=types.InlineKeyboardMarkup(
                        inline_keyboard=[
                            [types.InlineKeyboardButton(text="❌", callback_data="OK")]
                        ]
                    ),
                )
                logger.info(f"User {sub.admin_id} was notified about expiration")
            if days_left < 0:
                await clean_subscription(session, sub.admin_id, db)
        except TelegramForbiddenError:
            logger.info(
                f"Admin {sub.admin_id} has blocked the main bot. Marking as inactive."
            )
            await db.bot_api.change_user_status(session, sub.admin_id, False)
            if days_left < 0:
                await clean_subscription(session, sub.admin_id, db)
        except Exception as e:
            logger.error(
                f"An error occurred while checking subscription for admin {sub.admin_id}: {e}"
            )

    logger.info("APS completed subscriptions checking job")
