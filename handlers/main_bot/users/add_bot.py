import logging
from datetime import datetime, timezone
from typing import Any
from aiogram import Bot, html, types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramUnauthorizedError
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import OTHER_BOTS_URL, db
from main import bot as main_bot
from data.messages import messages
from utils import is_bot_token
from states import AddingBot
from filters import isSub
from keyboards.inline import bots_list

logger = logging.getLogger(__name__)
router = Router()


async def add_msg_to_state(state: FSMContext, message: types.Message):
    data = await state.get_data()
    sent_messages: list = data.get("msgs")
    sent_messages.append(message.message_id)
    await state.update_data(msgs=sent_messages)


@router.callback_query(F.data == "create_bot")
async def create_bot(
    call: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    bots = await db.admin_api.get_admins_bots(session, call.from_user.id)

    if len(bots) > 1 and not await isSub.__call__(isSub(), call, session):
        return

    sent_messages = []
    first_msg = call.message.message_id
    second_msg = await call.message.answer(messages["add_bot"])
    sent_messages.append(first_msg)
    sent_messages.append(second_msg.message_id)
    await state.set_state(AddingBot.token)
    await state.update_data(msgs=sent_messages)

    await call.answer()


@router.message(AddingBot.token, F.text.func(is_bot_token))
async def add_bot(
    message: types.Message, state: FSMContext, bot: Bot, session: AsyncSession
) -> Any:
    token = str(message.text)
    logger.info(f"Checking token {token} ...")
    new_bot = Bot(token=token, session=bot.session, parse_mode="HTML")

    try:
        bot_user = await new_bot.get_me()
    except TelegramUnauthorizedError:
        logger.info("Error: Token Unauthorized")
        third_msg = await message.answer(
            "<i>Этот токен уже занят.</i>",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="OK", callback_data="ok_error")]
                ]
            ),
        )

        await add_msg_to_state(state, third_msg)

        await message.delete()
        return

    await new_bot.delete_webhook(drop_pending_updates=True)
    await new_bot.set_webhook(
        OTHER_BOTS_URL.format(bot_token=token),
        allowed_updates=["message", "callback_query", "my_chat_member", "chat_member"],
    )
    logger.info("Set webhook for new bot")

    user = message.from_user

    admin = await db.admin_api.get_admin(session=session, admin_id=user.id)
    sub = await db.subscription_api.get_subscription(session, user.id)
    is_premium = (
        True
        if (sub is not None and sub.end_date > datetime.now(timezone.utc))
        else False
    )
    try:
        bot = await db.bot_api.add_bot(
            session=session,
            bot_id=bot_user.id,
            name=str(bot_user.full_name),
            url=str(bot_user.username),
            language_code=admin.language_code,
            admin_id=admin.id,
            token=token,
            is_premium=is_premium,
        )
    except:
        logger.info("Error: Token is already exists in database")
        third_msg = await message.answer(
            "<i>Этот токен уже занят.</i>",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="OK", callback_data="ok_error")]
                ]
            ),
        )

        await add_msg_to_state(state, third_msg)

        await message.delete()
        return

    logger.info(f"Added bot's information to DB (admin: {admin.id})")

    third_msg = await message.answer(
        "✅ Бот был успешно создан! "
        f"Перейдите в <b>{html.link('него', 'https://t.me/' + str(bot_user.username))}</b> "
        "и напишите команду /start, чтобы начать получать "
        "сообщения от пользователей.",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="OK", callback_data="ok_added")]
            ]
        ),
        disable_web_page_preview=True,
    )

    await add_msg_to_state(state, third_msg)

    await message.delete()
    return


@router.callback_query(F.data.in_(["ok_added", "ok_error"]))
async def ok_added(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    sent_messages: list = data.get("msgs")
    chat_id = call.from_user.id
    await main_bot.delete_message(chat_id, message_id=sent_messages[1])
    await main_bot.delete_message(chat_id, message_id=sent_messages[2])
    await state.clear()
    bots = await db.admin_api.get_admins_bots(
        session=session, admin_id=call.from_user.id
    )
    markup = await bots_list(bots)
    if not str(call.data) == "ok_error":
        await main_bot.edit_message_reply_markup(
            chat_id, message_id=sent_messages[0], reply_markup=markup
        )


@router.message(AddingBot.token)
async def delete_not_token(message: types.Message):
    await message.delete()
