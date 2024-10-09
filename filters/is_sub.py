import logging
from datetime import datetime, timezone
from aiogram.types import CallbackQuery
from aiogram.filters import BaseFilter
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import db
from data.messages import messages
from utils import clean_subscription

logger = logging.getLogger(__name__)


class isSub(BaseFilter):
    async def __call__(self, call: CallbackQuery, session: AsyncSession):
        admin_id = call.from_user.id
        sub = await db.subscription_api.get_subscription(session, admin_id)

        if sub is not None and sub.end_date > datetime.now(timezone.utc):
            logger.info(
                "CallbackQuery is considered to be from user with paid subscription"
            )
            return True
        elif sub is not None and sub.end_date < datetime.now(timezone.utc):
            logger.info("Deleting expired subscription...")
            await clean_subscription(session, admin_id, db)
            await call.answer(text="⚠️Срок подписки истек!", show_alert=True)

        logger.info("Ths user hasn't paid subscription")
        await call.answer(messages["ru"]["not_sub"], show_alert=True)
        return False
