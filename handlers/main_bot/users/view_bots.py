from aiogram import types, Router, F
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import db
from data.messages import messages
from keyboards.inline import bots_list

# from database.model import Admin

router = Router()


@router.callback_query(F.data == "view_bots")
async def view_bots(call: types.CallbackQuery, session: AsyncSession):
    bots = await db.admin_api.get_admins_bots(
        session=session, admin_id=call.from_user.id
    )
    # admin: Admin = await db.admin_api.get_admin(session=session,
    #                        admin_id=call.from_user.id)
    # lang = admin.language_code
    # lang = "ru"

    markup = await bots_list(bots)

    await call.message.edit_text(messages["bots_list"], reply_markup=markup)


@router.callback_query(F.data[:9] == "bots_page")
async def process_bots_page_callback(call: types.CallbackQuery, session: AsyncSession):
    page = int(call.data.split()[1])
    bots = await db.admin_api.get_admins_bots(
        session=session, admin_id=call.from_user.id
    )

    markup = await bots_list(bots, page)
    await call.message.edit_reply_markup(reply_markup=markup)
