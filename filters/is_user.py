import logging
from aiogram.types import Message
from aiogram.filters import BaseFilter
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import db

logger = logging.getLogger(__name__)

class isUser(BaseFilter):
    async def __call__(self, message: Message,
                       session: AsyncSession):
        user_id = message.from_user.id
        bot_id = message.bot.id

        sender = await db.sender_api.get_sender(session, sender_id=user_id)
        if sender is None:
            await db.sender_api.add_sender(session=session, user_id=user_id,
                                first_name=message.from_user.first_name,
                                bot_id=bot_id)
        elif sender.bot_id is None:
            await db.sender_api.add_bot_to_sender(session,
                                       sender_id=user_id,
                                       bot_id=bot_id)

        sender = await db.sender_api.get_sender(session, sender_id=user_id)
        admins = await db.bot_api.get_bots_admins(session=session,
                               bot_id=bot_id)

        if user_id in admins:
            return False
        logger.info("Message is considered to be from user")
        return True

