from aiogram.types import Message
from aiogram.filters import BaseFilter

from data.config import CREATORS
from utils import logger


class isBotCreator(BaseFilter):
    async def __call__(self, message: Message):

        if message.from_user.id in CREATORS:
            logger.info("filters/is_bot_creator returned True")
            return True
        return False

