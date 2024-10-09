import logging
from aiogram import Bot, types, Router, F
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import OTHER_BOTS_URL, db
from keyboards.inline import bots_list
from utils import is_main_admin

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data[:6] == "switch")
async def switch_bot_state(call: types.CallbackQuery, bot: Bot, session: AsyncSession):
    bot_id = int(str(call.data)[7:])
    db_bot = await db.bot_api.get_bot(session=session, bot_id=bot_id)
    token = db_bot.token
    status = db_bot.is_active
    bot = Bot(token=token, session=bot.session)

    if not await is_main_admin(call, session, db, bot_id):
        return

    await bot.delete_webhook(drop_pending_updates=True)

    if status:
        new_status = False
        answer = "✅Бот был успешно остановлен!"
        logger.info(f"Bot {db_bot.id} was stopped.")

    else:
        new_status = True
        answer = "✅Бот был успешно запущен!"

        await bot.set_webhook(
            OTHER_BOTS_URL.format(bot_token=token),
            allowed_updates=[
                "message",
                "callback_query",
                "my_chat_member",
                "chat_member",
            ],
        )
        logger.info(f"Bot {db_bot.id} was continued from being paused.")

    await db.bot_api.update_bot_field(
        session=session, bot_id=bot_id, field_name="is_active", new_value=new_status
    )

    bots = await db.admin_api.get_admins_bots(
        session=session, admin_id=call.from_user.id
    )
    markup = await bots_list(bots)
    await call.answer(answer, show_alert=True)
    return await call.message.edit_reply_markup(
        inline_message_id=call.inline_message_id, reply_markup=markup
    )
