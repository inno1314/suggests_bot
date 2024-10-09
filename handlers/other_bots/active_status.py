from aiogram import Router
from aiogram.types import ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter, MEMBER, KICKED
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import db

router = Router()


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def mark_as_inactive(event: ChatMemberUpdated, session: AsyncSession):
    await db.bot_api.change_user_status(session, event.from_user.id, new_status=False)


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def mark_as_active(event: ChatMemberUpdated, session: AsyncSession):
    await db.bot_api.change_user_status(session, event.from_user.id, new_status=True)
