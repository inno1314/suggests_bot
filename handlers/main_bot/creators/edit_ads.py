from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from utils import image_uploader
from data.config import db, BOT_TOKEN
from data.messages import messages
from keyboards.inline import back_markup
from states import Ads

router = Router()


@router.callback_query(F.data == "edit_ads")
async def view_ads(call: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    current_ad_message = await db.ads_api.get_ad_message(session)
    text = current_ad_message.html_text + messages["edit_ads"]

    await state.set_state(Ads.editing)

    if current_ad_message.photo_link is None:
        new_message = await call.message.edit_text(text=text, reply_markup=back_markup)
    else:
        new_message = await call.bot.send_photo(
            chat_id=call.from_user.id,
            photo=current_ad_message.photo_link,
            caption=text,
            reply_markup=back_markup,
        )
    await state.update_data(message_id=new_message.message_id)
    await call.message.delete()


@router.message(Ads.editing)
async def edit_ads(message: types.Message, session: AsyncSession, state: FSMContext):
    new_text = message.html_text
    link = image_uploader(message, BOT_TOKEN) if message.photo else None
    await db.ads_api.edit_ad_message(session, new_text, link)

    data = await state.get_data()
    message_id = int(data.get("message_id"))

    current_ad_message = await db.ads_api.get_ad_message(session)
    text = current_ad_message.html_text + messages["edit_ads"]

    await message.delete()
    await message.bot.delete_message(message.from_user.id, message_id)
    if current_ad_message.photo_link:
        new_message = await message.answer_photo(
            photo=current_ad_message.photo_link, caption=text, reply_markup=back_markup
        )
        await state.update_data(message_id=new_message.message_id)
        return
    new_message = await message.answer(text, reply_markup=back_markup)
    await state.update_data(message_id=new_message.message_id)
