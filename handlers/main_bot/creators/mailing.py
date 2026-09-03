import asyncio
import logging
from aiogram import types, F, Router, Bot
from aiogram.exceptions import TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
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
async def start_mailing(
    message: types.Message, bot: Bot, session: AsyncSession, state: FSMContext
):
    text = message.html_text
    photo_bytes = None
    if message.photo:
        try:
            file_io = await bot.download(message.photo[-1])
            if file_io:
                photo_bytes = file_io.read()
        except Exception as e:
            logger.error(f"Failed to download photo for mailing: {e}")

    status_msg = await message.answer("⏳ Начинаю рассылку по пользователям ботов...")

    bots = await db.bot_api.get_bots_for_mailing(session)
    bots_log = [b.id for b in bots]
    logger.info(f"Obtained from DB bot IDs for mailing: {bots_log}")

    success_count = 0
    fail_count = 0

    for db_bot in bots:
        tg_bot = Bot(token=db_bot.token, session=bot.session)
        users_to_mail = await db.bot_api.get_senders_for_mailing(session, db_bot.id)
        logger.info(
            f"Obtained from DB user IDs for mailing (bot {db_bot.id}): {len(users_to_mail)} users"
        )
        for user_id in users_to_mail:
            try:
                if photo_bytes is not None:
                    photo_file = types.BufferedInputFile(photo_bytes, filename="photo.jpg")
                    await tg_bot.send_photo(
                        chat_id=user_id, photo=photo_file, caption=text, parse_mode="HTML"
                    )
                else:
                    await tg_bot.send_message(
                        chat_id=user_id, text=text, parse_mode="HTML"
                    )
                success_count += 1
                await asyncio.sleep(0.05)
            except Exception as e:
                await db.bot_api.change_user_status(session, user_id, False)
                logger.info(
                    f"An error occurred while trying to send mailing message to {user_id} via bot {db_bot.id}: {e}"
                )
                fail_count += 1

    await state.clear()
    await status_msg.edit_text(
        f"✅ <b>Рассылка по пользователям завершена!</b>\n\n"
        f"🤖 Ботов задействовано: <code>{len(bots)}</code>\n"
        f"🟢 Успешно отправлено: <code>{success_count}</code>\n"
        f"🔴 Ошибок: <code>{fail_count}</code>",
        reply_markup=back_markup,
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
    photo_file_id = message.photo[-1].file_id if message.photo else None

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
            if photo_file_id is not None:
                await bot.send_photo(
                    chat_id=admin_id, photo=photo_file_id, caption=text, parse_mode="HTML"
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
