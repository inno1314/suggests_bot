import logging
from aiogram import types, Router, F
from aiogram.filters import Command, or_f
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import db

logger = logging.getLogger(__name__)
router = Router()


@router.message(or_f(Command("rm"), F.text == "🧹 Очистить предложку"))
async def clean_feed(message: types.Message, session: AsyncSession):
    bot = message.bot
    feed = await db.message_api.clean_feed(session, bot.id)
    logger.info(
        f"Obtained feed message's IDs from DB: {[message.id for message in feed]}"
    )
    for msg in feed:
        try:
            await bot.delete_message(chat_id=msg.chat_id, message_id=msg.id)
            logger.info(f"Deleting message {msg.id} ...")
        except Exception as e:
            logger.info(
                f"Exception when cleaning feed: {e}"
            )

    await message.delete()
