import logging
from aiogram import types, Bot, html, Router, F
from aiogram.filters.chat_member_updated import (
    ChatMemberUpdatedFilter,
    JOIN_TRANSITION,
    LEAVE_TRANSITION,
)

from data.config import db
from keyboards.inline import ok_button
from sqlalchemy.ext.asyncio import AsyncSession


logger = logging.getLogger(__name__)
router = Router()


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION),
    F.chat.type.in_({"channel"}),
)
async def bot_added_to_channel(
    event: types.ChatMemberUpdated, session: AsyncSession, bot: Bot
):
    """
    Бота добавили в канал

    :param event: event от Telegram типа "my_chat_member"
    :param bot: Bot
    :return:
    """
    chat_id = event.chat.id
    chat_name = event.chat.full_name
    bot_id = bot.id

    admins = await db.bot_api.get_bots_admins(session, bot_id)
    for admin in admins:
        await bot.send_message(
            chat_id=admin,
            text=f'ℹ️ Канал "{html.bold(chat_name)}" теперь доступен для публикаций постов из этого бота!',
            reply_markup=ok_button,
        )

    await db.channel_api.add_channel(
        session, channel_id=chat_id, name=chat_name, bot_id=bot_id
    )
    logger.info(f"Added channel {chat_name} ({chat_id}) to bot {bot_id}")


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=LEAVE_TRANSITION),
    F.chat.type.in_({"channel"}),
)
async def bot_deleted_from_channel(
    event: types.ChatMemberUpdated, session: AsyncSession, bot: Bot
):
    """
    Бота удалили из канала

    :param event: event от Telegram типа "my_chat_member"
    :param bot: Bot
    :return:
    """
    chat_id = event.chat.id
    name = event.chat.full_name
    bot_id = bot.id

    admins = await db.bot_api.get_bots_admins(session, bot_id)
    for admin in admins:
        await bot.send_message(
            chat_id=admin,
            text=f'⚠️ Канал "{html.bold(name)}" более недоступен для публикации постов из этого бота!',
            reply_markup=ok_button,
        )

    await db.channel_api.remove_channel(
        session=session, channel_id=chat_id, bot_id=bot_id
    )
    logger.info(f"Removed channel {chat_id} from bot {bot_id}")
