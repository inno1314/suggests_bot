import asyncio
import logging
from aiogram import types, F, Router, Bot
from aiogram.exceptions import TelegramForbiddenError
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


@router.callback_query(F.data == "active_admins_mailing")
async def ask_active_admins_mailing(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(Mailing.active_admins)
    await call.message.edit_text(
        text=messages["start_active_admins_mailing"], reply_markup=back_markup
    )


@router.message(Mailing.active_admins)
async def start_active_admins_mailing(
    message: types.Message, bot: Bot, session: AsyncSession, state: FSMContext
):
    text = message.html_text
    link = image_uploader(message) if message.photo else None

    status_msg = await message.answer(
        "⏳ Собираю список администраторов активных ботов..."
    )

    admins_to_mail = await db.admin_api.get_active_bots_admins(session, days=30)
    logger.info(
        f"Obtained from DB active admin IDs for mailing: {admins_to_mail} (count: {len(admins_to_mail)})"
    )

    if not admins_to_mail:
        await status_msg.edit_text(
            "⚠️ Не найдено администраторов активных ботов для рассылки.",
            reply_markup=back_markup,
        )
        await state.clear()
        return

    await status_msg.edit_text(
        f"⏳ Начинаю рассылку для {len(admins_to_mail)} администраторов..."
    )

    success_count = 0
    fail_count = 0

    for admin_id in admins_to_mail:
        try:
            if link is not None:
                await bot.send_photo(
                    chat_id=admin_id, photo=link, caption=text, parse_mode="HTML"
                )
            else:
                await bot.send_message(
                    chat_id=admin_id, text=text, parse_mode="HTML"
                )
            success_count += 1
            await asyncio.sleep(0.05)
        except TelegramForbiddenError:
            logger.info(f"Admin {admin_id} has blocked the bot. Marking as inactive.")
            await db.bot_api.change_user_status(session, admin_id, False)
            fail_count += 1
        except Exception as e:
            logger.info(
                f"An error occurred while trying to send mailing message to admin {admin_id}: {e}"
            )
            fail_count += 1

    await state.clear()
    await status_msg.edit_text(
        f"✅ <b>Рассылка по администраторам активных ботов завершена!</b>\n\n"
        f"👥 Всего получателей: <code>{len(admins_to_mail)}</code>\n"
        f"🟢 Успешно отправлено: <code>{success_count}</code>\n"
        f"🔴 Ошибок: <code>{fail_count}</code>",
        reply_markup=back_markup,
    )
    await message.delete()
