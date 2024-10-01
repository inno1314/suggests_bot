from datetime import datetime, timezone
from aiogram.types import CallbackQuery
from aiogram.filters import BaseFilter
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import db
from utils import logger, clean_subscription


class isAdminQuery(BaseFilter):
    async def __call__(self, call: CallbackQuery,
                       session: AsyncSession):
        admins = await db.bot_api.get_bots_admins(session=session,
                               bot_id=call.bot.id)
        print(admins)
        sub = await db.subscription_api.get_subscription(session, admins[0])

        if sub is not None and sub.end_date < datetime.now(timezone.utc):
            logger.info("filters/is_sub deleted expired subscription")
            await clean_subscription(session, admins[0], db)
            await call.answer(text="⚠️Срок подписки истек!", show_alert=True)
            return False

        if call.from_user.id in admins:
            logger.info("filters/admins_query returned True")
            return True
        return False

