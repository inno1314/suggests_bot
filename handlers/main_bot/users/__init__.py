__all__ = ("router",)

from aiogram import Router

from .start import router as start_router
from .view_bots import router as view_bots_router
from .add_bot import router as add_bot_router
from .delete_bot import router as delete_bot_router
from .switch_bot_state import router as switch_state_router
from .back import router as back_router
from .settings import router as setts_router
from .get_subscription import router as get_sub
from .ok_button import router as ok_router
from aiogram.filters import ChatMemberUpdatedFilter, MEMBER, KICKED
from aiogram.types import ChatMemberUpdated
from sqlalchemy.ext.asyncio import AsyncSession
from data.config import db

router = Router(name=__name__)

router.include_routers(start_router,
                       view_bots_router,
                       add_bot_router,
                       delete_bot_router,
                       switch_state_router,
                       back_router,
                       setts_router,
                       get_sub,
                       ok_router)



@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def mark_as_inactive(event: ChatMemberUpdated, session: AsyncSession):
    await db.bot_api.change_user_status(session, event.from_user.id, new_status=False)


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def mark_as_active(event: ChatMemberUpdated, session: AsyncSession):
    await db.bot_api.change_user_status(session, event.from_user.id, new_status=True)
