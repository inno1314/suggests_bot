import logging
import re
from aiogram import F, types, Router
from aiogram.filters import CommandStart, CommandObject
from sqlalchemy.ext.asyncio import AsyncSession

from data.messages import messages
from data.config import db
from keyboards.inline import start_msg_markup

logger = logging.getLogger(__name__)
router = Router()


@router.message(
    CommandStart(deep_link=True, magic=F.args.regexp(re.compile(r"code_(\d+)")))
)
@router.message(CommandStart())
async def add_invited_admin(
    message: types.Message, session: AsyncSession, command: CommandObject
):
    user = message.from_user
    admin = await db.admin_api.get_admin(session=session, admin_id=user.id)
    if admin is None:
        admin = await db.admin_api.add_admin(
            session=session,
            admin_id=user.id,
            name=user.first_name,
            language_code=user.language_code,
        )
        logger.info(f"Added admin {user.id} to DB")

    if command.args is not None:
        code = command.args.split("_")[1]
        bot_id = await db.codes_api.use_code(session, code)
        if bot_id is not None:
            await db.bot_api.add_admin(session, bot_id, admin_id=user.id)

    await message.answer(messages["start"], reply_markup=start_msg_markup)
