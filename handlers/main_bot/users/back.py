from aiogram import types, F, Router
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import db
from data.messages import messages
from keyboards.inline import start_msg_markup
from .get_subscription import get_premium
from .view_bots import view_bots

router = Router()


@router.callback_query(F.data == "to_menu")
async def to_menu(call: types.CallbackQuery):
    await call.message.edit_text(messages["start"], reply_markup=start_msg_markup)


@router.callback_query(F.data == "to_botlist")
async def to_botlist(call: types.CallbackQuery, session: AsyncSession):
    await view_bots(call, session)


@router.callback_query(F.data.in_(["to_sub_plans", "cancel_payment"]))
async def to_sub_plans(call: types.CallbackQuery, session: AsyncSession):
    if call.data == "cancel_payment":
        await db.admin_api.assign_admin_label(session, call.from_user.id, "None")
    await get_premium(call, session)
