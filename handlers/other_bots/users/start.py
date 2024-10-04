import logging
from aiogram import types, Router
from aiogram.filters import Command
from data.config import db
from sqlalchemy.ext.asyncio import AsyncSession

from data.messages import messages

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("start"))
async def start(message: types.Message, session: AsyncSession):
    user_id = message.from_user.id
    bot_id = message.bot.id
    sender = await db.sender_api.get_sender(session, sender_id=user_id)
    if not sender:
        logger.info(f"Adding sender {user_id} to DB...")
        await db.sender_api.add_sender(session=session, user_id=user_id,
                            first_name=message.from_user.first_name,
                            bot_id=bot_id)
    elif not sender.bot_id:
        await db.sender_api.add_bot_to_sender(session,
                                   sender_id=user_id,
                                   bot_id=bot_id)
        logger.info(f"Added bot {bot_id} to sender {user_id}")

    await message.bot.delete_my_commands(scope=types.BotCommandScopeChat(chat_id=user_id))

    db_bot = await db.bot_api.get_bot(session, bot_id)
    text = db_bot.start_message if db_bot.start_message is not None \
        else messages['ru']['senders_start']
    await message.answer(text)

