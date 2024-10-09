import logging
from aiogram.types import Message
from aiogram.filters import BaseFilter

from data.config import CREATORS

logger = logging.getLogger(__name__)


class isBotCreator(BaseFilter):
    async def __call__(self, message: Message):

        if message.from_user.id in CREATORS:
            logger.info("Message is considered to be from CREATOR")
            return True
        return False
