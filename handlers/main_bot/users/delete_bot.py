import logging
from typing import Any
from aiogram import Bot, types, Router, F
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import db
from keyboards.inline import bots_list
from utils import is_main_admin

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data[:3] == "del")
async def delete_bot(call: types.CallbackQuery, bot: Bot, session: AsyncSession) -> Any:
    bot_id = int(str(call.data)[4:])
    db_bot = await db.bot_api.get_bot(session=session, bot_id=bot_id)
    token = db_bot.token
    bot = Bot(token=token, session=bot.session)

    # admins = await db.bot_api.get_bots_admins(session=session,
    #                            bot_id=bot_id)

    if not await is_main_admin(call, session, db, bot_id):
        return

    bot_user = await bot.get_me()
    await bot.delete_my_commands()
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info(f"Deleted webhook for bot {bot_user.id}")

    await db.message_api.clean_feed(session, bot_user.id)
    await db.bot_api.delete_bot(session=session, bot_id=bot_user.id)
    logger.info(f"Deleted bot {bot_user.id} from database")

    bots = await db.admin_api.get_admins_bots(
        session=session, admin_id=call.from_user.id
    )
    markup = await bots_list(bots)

    await call.answer(
        f"✅Бот {bot_user.username} был успешно остановлен и удалён!", show_alert=True
    )
    return await call.message.edit_reply_markup(
        inline_message_id=call.inline_message_id, reply_markup=markup
    )
