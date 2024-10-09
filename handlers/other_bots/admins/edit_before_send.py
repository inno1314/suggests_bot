from aiogram import types, Router, F, html
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from .recieve_actions import hide_channels
from data.config import db
from keyboards.inline import channels_list, cancel_edit_button
from states import EditBeforeSend, PublishMedia

router = Router()


@router.callback_query(PublishMedia.messages, F.data == "edit_before_send")
async def edit_before_send(call: types.CallbackQuery, state: FSMContext):
    await hide_channels(call)
    msg_to_delete = await call.message.answer(
        text=f"{html.italic('Отправьте отредактированное сообщение:')}",
        reply_markup=cancel_edit_button,
    )

    await state.set_state(EditBeforeSend.editing)
    await state.update_data(bot_id=call.bot.id)
    await state.update_data(msg_to_delete=msg_to_delete.message_id)
    await call.answer()


@router.callback_query(EditBeforeSend.editing, F.data == "cancel_edit")
async def cancel_edit(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg_to_delete = int(data.get("msg_to_delete"))
    await call.bot.delete_message(call.from_user.id, msg_to_delete)
    await state.clear()
    await call.answer()


@router.message(EditBeforeSend.editing)
async def get_edited_message(
    message: types.Message,
    state: FSMContext,
    session: AsyncSession,
    album: list[types.Message] | None = None,
):
    data = await state.get_data()
    bot_id = int(data.get("bot_id"))
    channels = await db.channel_api.get_channels_info(session=session, bot_id=bot_id)

    await state.set_state(EditBeforeSend.sending)
    if album is not None:
        await state.update_data(media_group_ids=[msg.message_id for msg in album])
    else:
        await state.update_data(message_id=message.message_id)

    markup = await channels_list(channels)
    await message.answer(
        text=f"{html.italic('Выберите канал для публикации:')}", reply_markup=markup
    )


@router.callback_query(EditBeforeSend.sending, F.data[:7] == "send_to")
async def send_to(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    user_id = call.from_user.id
    bot: Bot = call.bot
    call_data = call.data.split()
    chat_id = int(call_data[1])

    data = await state.get_data()
    msg_to_delete = int(data.get("msg_to_delete"))
    group_id = str(data.get("group_id"))
    message_id = data.get("message_id")
    media_group_ids = data.get("media_group_ids")

    channel = await db.channel_api.get_channel(session, chat_id, bot.id)
    group = await db.message_api.get_messages_by_group_id(session, bot.id, group_id)
    sender_id = group[0].sender_id

    if media_group_ids is not None and type(media_group_ids) == list:
        await bot.copy_messages(
            chat_id=chat_id, from_chat_id=user_id, message_ids=media_group_ids
        )
        await bot.delete_messages(user_id, media_group_ids)
    elif message_id is not None:
        await bot.copy_message(
            chat_id=chat_id, from_chat_id=user_id, message_id=int(message_id)
        )
        await bot.delete_message(user_id, message_id)
    await call.message.delete()
    await bot.delete_message(user_id, msg_to_delete)

    await bot.send_message(
        chat_id=sender_id,
        text=f"⭐️ Администрация опубликовала Ваше сообщение в  \
        канале <b>'{channel.name}'</b>!",
    )
    await state.clear()
    await call.answer()


@router.callback_query(EditBeforeSend.sending, F.data == "cancel_editing")
async def cancel_editing(call: types.CallbackQuery, state: FSMContext):
    bot: Bot = call.bot
    user_id = call.from_user.id

    data = await state.get_data()
    msg_to_delete = int(data.get("msg_to_delete"))
    message_id = int(data.get("message_id"))

    await bot.delete_message(user_id, message_id)
    await bot.delete_message(user_id, msg_to_delete)
    await call.message.delete()
    await state.clear()
    await call.answer()
