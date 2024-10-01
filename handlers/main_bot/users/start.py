import re
from aiogram import F, types, Router
from aiogram.filters import CommandStart, CommandObject
from sqlalchemy.ext.asyncio import AsyncSession

from data.messages import messages
from data.config import db, other_bots_commands as commands
from keyboards.inline import start_msg_markup
from utils import logger

router = Router()

@router.message(CommandStart(
    deep_link=True, magic=F.args.regexp(re.compile(r'code_(\d+)'))
))
@router.message(CommandStart())
async def add_invited_admin(message: types.Message, session: AsyncSession,
                            command: CommandObject):
    user = message.from_user
    bot = message.bot
    # lang = str(user.language_code)
    lang = 'ru'
    admin = await db.admin_api.get_admin(session=session, admin_id=user.id)
    if admin is None:
         admin = await db.admin_api.add_admin(
            session=session, admin_id=user.id,
            name=user.first_name,
            language_code=user.language_code)
         logger.info(f"added admin {user.id} to db")

    if command.args is not None:
        code = command.args.split("_")[1]
        bot_id = await db.codes_api.use_code(session, code)
        if bot_id is not None:
            await db.bot_api.add_admin(session, bot_id,
                                       admin_id=user.id)
    
    await message.answer(messages[lang]["start"],
                         reply_markup=start_msg_markup)

