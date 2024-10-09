import json
from aiogram import types, Router, F, html, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import db
from .recieve_actions import hide_channels
from utils.restore_helper import restore_album
from utils import deserialize_telegram_object_to_python
from keyboards.inline import channels_list, cancel_edit_button
from models.message import MessageModel
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
    msg_to_delete = int(data["msg_to_delete"])
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
    bot_id = int(data["bot_id"])
    channels = await db.channel_api.get_channels_info(session=session, bot_id=bot_id)
    await state.set_state(EditBeforeSend.sending)

    if album is not None:
        await state.update_data(album_size=len(album))
        album.sort(key=lambda m: m.message_id)
        for index, album_message in enumerate(album, 0):
            model = album_message.model_dump_json()
            await state.update_data({f"{index}message_model": model})
            if len(album_message.html_text) > 0:
                print(album_message.html_text, type(album_message.html_text))
                await state.update_data(html_text=album_message.html_text)

        await state.update_data(media_group_ids=[msg.message_id for msg in album])
    else:
        try:
            model = message.model_dump_json()
        except:
            json_model = deserialize_telegram_object_to_python(
                message, default=DefaultBotProperties()
            )
            model = json.dumps(json_model)

        await state.update_data({"message_model": model})
        if len(message.html_text) > 0:
            await state.update_data(html_text=message.html_text)
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
    group = await db.message_api.get_messages_by_group_id(
        session, bot.id, str(data.get("group_id"))
    )
    channel = await db.channel_api.get_channel(session, chat_id, bot.id)

    db_bot = await db.bot_api.get_bot(session, bot.id)
    formatting = (
        "\n\n" + db_bot.post_formatting if db_bot.post_formatting is not None else ""
    )

    media_group_ids = data.get("media_group_ids")
    message_id = data.get("message_id")
    message_model = data.get("message_model")

    if data.get("album_size") is not None:
        media = list()
        for index in range(int(data["album_size"])):
            model_from_data = data[f"{index}message_model"]
            message_data = json.loads(model_from_data)
            model = MessageModel.model_validate(message_data)
            restored_media = model.to_aiogram()
            media.append(restored_media)

        print(data.get("html_text"), str(data.get("html_text")))
        caption = (
            str(data.get("html_text")) if data.get("html_text") is not None else ""
        )

        new_album = restore_album(messages=media, sign=formatting, html_text=caption)
        await bot.send_media_group(chat_id, media=new_album)

        if media_group_ids is not None:
            await bot.delete_messages(user_id, media_group_ids)

    if message_id is not None and message_model is not None:
        message_data = json.loads(message_model)
        model = MessageModel.model_validate(message_data)
        restored_message = model.to_aiogram()
        if restored_message.text is not None:
            text = (
                str(data.get("html_text")) if data.get("html_text") is not None else ""
            )
            await bot.send_message(
                chat_id, text + formatting, disable_web_page_preview=True
            )
        else:
            caption = (
                restored_message.html_text + formatting
                if restored_message.caption is not None
                else formatting
            )
            await restored_message.copy_to(chat_id, caption=caption).as_(bot)

        await bot.delete_message(user_id, int(message_id))

    await call.message.delete()
    await bot.delete_message(user_id, int(data["msg_to_delete"]))

    sender_id = group[0].sender_id
    await bot.send_message(
        chat_id=sender_id,
        text=f"⭐️ Администрация опубликовала Ваше сообщение в  \
        канале <b>'{channel.name}'</b>!",
    )
    await state.clear()
    await call.answer()


@router.callback_query(EditBeforeSend.sending, F.data == "cancel_publish")
async def cancel_editing(call: types.CallbackQuery, state: FSMContext):
    bot: Bot = call.bot
    user_id = call.from_user.id

    data = await state.get_data()
    msg_to_delete = int(data["msg_to_delete"])
    message_id = data.get("message_id")
    media_group_ids = data.get("media_group_ids")

    if media_group_ids is not None and type(media_group_ids) == list:
        await bot.delete_messages(user_id, media_group_ids)
    elif message_id is not None:
        await bot.delete_message(user_id, message_id)

    await bot.delete_message(user_id, msg_to_delete)
    await call.message.delete()
    await state.clear()
    await call.answer()
