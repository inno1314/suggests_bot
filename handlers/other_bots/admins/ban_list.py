import logging
from aiogram import types, Router, F
from aiogram.filters import Command, or_f
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline import ok_button, banned_buttons
from data.config import db

logger = logging.getLogger(__name__)
router = Router()


async def show_banned(message: types.Message, session: AsyncSession, page: int) -> None:
    """
    Показывает список заблокированных юзеров
    :param message: types.Message
    :param session: AsyncSession
    :param page: Страница списка
    """
    bot_id = message.bot.id
    banlist = await db.bot_api.get_banlist(session, bot_id=bot_id)

    markup = await banned_buttons(session, banlist, page)
    await message.edit_reply_markup(
        text="📋 Список заблокированных пользователей:", reply_markup=markup
    )


@router.message(or_f(Command("banlist"), F.text == "🚷 Banlist"), F.chat.type == "private")
async def show_banlist(message: types.Message, session: AsyncSession) -> None:
    bot_id = message.bot.id
    banlist = await db.bot_api.get_banlist(session, bot_id=bot_id)
    await message.delete()
    if not banlist:
        await message.answer(
            text="📋 Список заблокированных пользователей пуст!", reply_markup=ok_button
        )
        return

    markup = await banned_buttons(session, banlist)
    await message.answer(
        text="📋 Список заблокированных пользователей:", reply_markup=markup
    )


@router.callback_query(F.data[:4] == "page")
async def change_banlist_page(call: types.CallbackQuery, session: AsyncSession):
    page = int(call.data.split()[1])
    await show_banned(call.message, session, page)


@router.callback_query(F.data[:5] == "unban")
async def unban_sender(call: types.CallbackQuery, session: AsyncSession):
    sender_id = int(call.data[6:])
    bot_id = call.bot.id

    await db.sender_api.change_block_status(session, sender_id, bot_id)
    logger.info(f"Sender {sender_id} was deleted from banlist")

    await show_banlist(call.message, session)
