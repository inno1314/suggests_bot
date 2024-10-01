import logging
from aiogram.types import Message
from aiogram.filters import BaseFilter
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import db

logger = logging.getLogger(__name__)

class isAdmin(BaseFilter):
    async def __call__(self, message: Message,
                       session: AsyncSession):
        admins = await db.bot_api.get_bots_admins(session=session,
                               bot_id=message.bot.id)

        if message.from_user.id in admins:
            logger.info("Message is considered to be from admin")
            return True
        return False

