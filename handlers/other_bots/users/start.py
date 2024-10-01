from aiogram import types, Router
from aiogram.filters import Command
from data.config import db
from sqlalchemy.ext.asyncio import AsyncSession

from data.messages import messages
from utils import logger

router = Router()

@router.message(Command("start"))
async def start(message: types.Message, session: AsyncSession):
    user_id = message.from_user.id
    bot_id = message.bot.id
    sender = await db.sender_api.get_sender(session, sender_id=user_id)
    if not sender:
        await db.sender_api.add_sender(session=session, user_id=user_id,
                            first_name=message.from_user.first_name,
                            bot_id=bot_id)
        logger.info(f"adding sender {user_id} to db")
    elif not sender.bot_id:
        await db.sender_api.add_bot_to_sender(session,
                                   sender_id=user_id,
                                   bot_id=bot_id)
        logger.info(f"added bot_id {bot_id} to sender {user_id}")

    await message.bot.delete_my_commands(scope=types.BotCommandScopeChat(chat_id=user_id))
    await message.answer(messages['ru']['senders_start'])

