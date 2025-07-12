import logging
from aiogram import Bot, types, Router, F, html
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from models.message import MessageModel
from data.config import db
from data.messages import messages
from utils import restore_album, make_new_album
from keyboards.inline import channels_list, ok_button
from states import PublishMedia

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.reply_to_message.is_not(None))
async def answer_sender(
    message: types.Message,
    session: AsyncSession,
    album: list[types.Message] | None = None,
):
    bot: Bot = message.bot
    sender_id = await db.sender_api.get_sender_by_message(
        session=session, message_id=message.reply_to_message.message_id, bot_id=bot.id
    )
    if sender_id is None:
        await message.delete()
        await message.answer(
            "🚫 Не удалось отправить сообщение получателю!", reply_markup=ok_button
        )
        return

    try:
        await bot.send_message(
            chat_id=sender_id, text="Администрация ответила на ваше сообщение:"
        )

        if album:
            album.sort(key=lambda m: m.message_id)
            new_album = make_new_album(album, "")
            await bot.send_media_group(chat_id=sender_id, media=new_album)
            return

        await message.copy_to(chat_id=sender_id)
    except Exception as e:
        logger.info(f"Unable to send message to sender {sender_id}: {e}")
        await message.delete()
        await message.answer(
            "🚫 Не удалось отправить сообщение получателю!", reply_markup=ok_button
        )
        return

    await message.delete()


@router.callback_query(F.data[:5].in_(["clear", "block"]))
async def clear_and_block(call: types.CallbackQuery, session: AsyncSession):
    bot: Bot = call.bot
    sender_id = int(call.data.split()[1])
    messages = await db.message_api.get_suggests(session=session, sender_id=sender_id)

    for message in messages:
        await bot.delete_message(message.chat_id, message.id)
        await db.message_api.delete_suggested_msg(session, message.id)
        logger.info(f"Deleting message {message.id} ...")

    if call.data[:5] == "block":
        await db.sender_api.change_block_status(session, sender_id, bot.id)


@router.callback_query(F.data[:7] == "del_msg")
async def clear_all(call: types.CallbackQuery, session: AsyncSession):
    bot: Bot = call.bot
    group_id = call.data.split()[1]
    group = await db.message_api.get_messages_by_group_id(session, bot.id, group_id)
    for message in group:
        logger.info(f"Deleting message {message.id} ...")
        try:
            await bot.delete_message(chat_id=message.chat_id, message_id=message.id)
        except:
            pass
        await db.message_api.delete_suggested_msg(session, message.id)


@router.callback_query(F.data[:7] == "publish")
async def publish(call: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    channels = await db.channel_api.get_channels_info(
        session=session, bot_id=call.bot.id
    )
    if len(channels) == 0:
        await call.answer(messages["no_channels"], show_alert=True)
        return

    group_id = call.data.split()[1]
    await state.set_state(PublishMedia.messages)
    await state.update_data(group_id=group_id)

    current_markup = call.message.reply_markup
    markup = await channels_list(channels, current_markup)
    await call.message.edit_reply_markup(reply_markup=markup)


@router.callback_query(PublishMedia.messages, F.data == "cancel_publish")
async def hide_channels(call: types.CallbackQuery):
    buttons = []
    markup = call.message.reply_markup
    for row in markup.inline_keyboard[:1]:
        for button in row:
            buttons.append(button)

    new_markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    new_markup.inline_keyboard.append(buttons)
    await call.message.edit_reply_markup(reply_markup=new_markup)


@router.callback_query(PublishMedia.messages, F.data[:7] == "send_to")
async def send_to(call: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    await hide_channels(call)
    bot: Bot = call.bot
    call_data = call.data.split()
    chat_id = int(call_data[1])

    data = await state.get_data()
    group_id = str(data.get("group_id"))

    group = await db.message_api.get_messages_by_group_id(session, bot.id, group_id)
    group = sorted(group, key=lambda msg: msg.id)
    sender_id = group[0].sender_id
    channel = await db.channel_api.get_channel(session, chat_id, bot.id)
    db_bot = await db.bot_api.get_bot(session, bot.id)

    model = MessageModel.model_validate(group[0].message_data)
    restored_message = model.to_aiogram()
    sender_name = restored_message.from_user.first_name

    formatting = (
        "\n\n" + db_bot.post_formatting if db_bot.post_formatting is not None else ""
    )
    signature = f"\n\n{html.code('👤 ' + sender_name)}" if db_bot.sign_messages else ""

    await bot.send_message(
        chat_id=sender_id,
        text=f"⭐️ Администрация опубликовала Ваше сообщение в  \
        канале <b>'{channel.name}'</b>!",
    )
    await state.clear()

    if group[0].media_group_id != "":
        media_group = await db.message_api.get_messages_by_media_group_id(
            session, bot.id, call.from_user.id, group[0].media_group_id
        )
        media_group = sorted(media_group, key=lambda msg: msg.id)

        media = list()
        for msg in media_group:
            model = MessageModel.model_validate(msg.message_data)
            restored_media = model.to_aiogram()
            media.append(restored_media)

        new_album = restore_album(
            media, sign=signature + formatting, html_text=group[0].html_text
        )
        await bot.send_media_group(chat_id, media=new_album)
        return

    if restored_message.text:
        text = group[0].html_text + signature + formatting
        return await bot.send_message(chat_id, text, disable_web_page_preview=True)

    caption = (
        group[0].html_text + signature + formatting
        if restored_message.caption is not None
        else signature
    )
    await restored_message.copy_to(chat_id, caption=caption).as_(bot)


@router.callback_query(F.data[:12] == "channel_page")
async def process_channel_page_callback(
    call: types.CallbackQuery, session: AsyncSession
):
    page = int(call.data.split()[1])
    channels = await db.channel_api.get_channels_info(session, call.bot.id)
    current_markup: types.InlineKeyboardMarkup = call.message.reply_markup
    markup = await channels_list(channels, current_markup, page)
    await call.message.edit_reply_markup(reply_markup=markup)
