from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from utils import image_uploader
from data.config import db
from data.messages import messages
from keyboards.inline import ads_markup
from states import Ads

router = Router()


@router.callback_query(F.data == "edit_ads")
async def view_ads(call: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    """TODO: Добавить возможность возвращать значение по умолчанию"""
    current_ad_message = await db.ads_api.get_ad_message(session)
    if current_ad_message is not None:
        text = current_ad_message.html_text + messages["edit_ads"]
    else:
        text = messages["default_answer"]+ messages["edit_ads"]
    await state.set_state(Ads.editing)

    if current_ad_message is None or current_ad_message.photo_link is None:
        new_message = await call.message.edit_text(text=text, reply_markup=ads_markup)
    else:
        await call.message.delete()
        new_message = await call.bot.send_photo(
            chat_id=call.from_user.id,
            photo=current_ad_message.photo_link,
            caption=text,
            reply_markup=ads_markup,
        )
    await state.update_data(message_id=new_message.message_id)


@router.message(Ads.editing)
async def edit_ads(message: types.Message, session: AsyncSession, state: FSMContext):
    new_text = message.html_text
    link = image_uploader(message) if message.photo else None
    await db.ads_api.edit_ad_message(session, new_text, link)

    data = await state.get_data()
    message_id = int(data["message_id"])

    current_ad_message = await db.ads_api.get_ad_message(session)
    text = current_ad_message.html_text + messages["edit_ads"]

    await message.delete()
    await message.bot.delete_message(message.from_user.id, message_id)
    if current_ad_message.photo_link:
        new_message = await message.answer_photo(
            photo=current_ad_message.photo_link, caption=text, reply_markup=ads_markup
        )
        await state.update_data(message_id=new_message.message_id)
        return
    new_message = await message.answer(text, reply_markup=ads_markup)
    await state.update_data(message_id=new_message.message_id)

@router.callback_query(Ads.editing, F.data == "clear_ads")
async def clear_ads(call: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    await db.ads_api.edit_ad_message(session, html_text=messages["default_answer"])

    data = await state.get_data()
    message_id = int(data["message_id"])

    await call.bot.delete_message(call.from_user.id, message_id)
    current_ad_message = await db.ads_api.get_ad_message(session)
    text = current_ad_message.html_text + messages["edit_ads"]

    new_message = await call.message.answer(text, reply_markup=ads_markup)
    await state.update_data(message_id=new_message.message_id)
