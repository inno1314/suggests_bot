import logging
from aiogram import types, F, Router, Bot
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from utils import image_uploader
from data.config import db
from data.messages import messages
from keyboards.inline import back_markup
from states import Mailing


logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "mailing")
async def ask_mailing(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(Mailing.start)
    await call.message.edit_text(
        text=messages["start_mailing"], reply_markup=back_markup
    )


@router.message(Mailing.start)
async def start_mailing(message: types.Message, bot: Bot, session: AsyncSession):
    text = message.html_text
    link = image_uploader(message) if message.photo else None

    bots = await db.bot_api.get_bots_for_mailing(session)
    bots_log = [bot.id for bot in bots]
    logger.info(f"Obtained from DB bot's IDs for mailing: {bots_log}")
    for db_bot in bots:
        tg_bot = Bot(token=db_bot.token, session=bot.session)
        users_to_mail = await db.bot_api.get_senders_for_mailing(session, db_bot.id)
        logger.info(f"Obtained from DB user's IDs for mailing: {users_to_mail}")
        for user_id in users_to_mail:
            try:
                if link is not None:
                    await tg_bot.send_photo(
                        chat_id=user_id, photo=link, caption=text, parse_mode="HTML"
                    )
                else:
                    await tg_bot.send_message(
                        chat_id=user_id, text=text, parse_mode="HTML"
                    )
            except Exception as e:
                await db.bot_api.change_user_status(session, user_id, False)
                logger.info(
                    f"An error occured while trying to send mailing message {e}"
                )

    await message.delete()
