import json
from aiogram import Bot, html, types, Router
from aiogram.client.default import DefaultBotProperties
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

# from models.message import MessageModel
from data.config import db
from data.messages import messages
from keyboards.inline import make_recive_options
from utils import logger, make_new_album, generate_id, \
    deserialize_telegram_object_to_python


router = Router()

async def send_with_kwargs(bot: Bot, session: AsyncSession, 
                           sender_id: int, kwargs: dict,
                           message: types.Message, data: Any):
    group_id: str | None = kwargs.pop("group_id")
    chat_id = int(kwargs.get("chat_id"))

    sent_message = await bot.send_message(**kwargs) if kwargs.get("caption") is None \
    else await message.copy_to(**kwargs)
    
    await db.message_api.add_message(session=session,
                         message_id=sent_message.message_id,
                         sender_id=sender_id,
                         chat_id=chat_id,
                         html_text=message.html_text,
                         data=data,
                         bot_id=bot.id,
                         group_id=group_id)
    logger.info(f"\n|added message with id: {sent_message.message_id} to db with group_id: {group_id}|")


@router.message()
async def resend_to_admin(message: types.Message, session: AsyncSession,
                          album: list[types.Message] | None = None):
    bot: Bot = message.bot
    sender_id = message.from_user.id
    sender_username = message.from_user.username

    admins = await db.bot_api.get_bots_admins(session, bot_id=bot.id)
    sender = await db.sender_api.get_sender(session, sender_id)
    db_bot = await db.bot_api.get_bot(session, bot_id=bot.id)
    group_id = generate_id()

    try:
        model = message.model_dump_json()
        json_model = json.loads(model)
    except:
        json_model = deserialize_telegram_object_to_python(
            message,
            default=DefaultBotProperties()
        )

    if sender.id in db_bot.banlist:
        await message.answer("Вы заблокированы! Ваши сообщения не будут отправляться.")
        logger.info(f"message from user {sender.id} was blocked")
        return

    for admin_id in admins:    
        markup = await make_recive_options(
            message_id=group_id,
            sender_id=sender_id,
            sender_username=sender_username)
        signature = f"\n\n{html.code('👤 '+message.from_user.first_name)}"
        kwargs = {
            "chat_id": admin_id,
            "reply_markup": markup,
            "group_id": group_id,
        }

        if album:
            album.sort(key=lambda m: m.message_id)
            new_album = make_new_album(album, sign=signature)
            list_of_sent = await bot.send_media_group(chat_id=admin_id,
                                                    media=new_album)

            for index, album_message in enumerate(album, 0):
                model = album_message.model_dump_json()
                json_model = json.loads(model)
                await db.message_api.add_message(session=session,
                                     message_id=list_of_sent[index].message_id,
                                     sender_id=sender_id,
                                     chat_id=admin_id,
                                     bot_id=bot.id,
                                     html_text=album_message.html_text,
                                     data=json_model,
                                     media_group_id=album_message.media_group_id,
                                     group_id=group_id,
                                     )

            ids_of_sent = [message.message_id for message in list_of_sent]
            logger.info(f"\n|added messages with ids: {ids_of_sent} to db with group_id: {group_id}|")
            markup = await make_recive_options(
                message_id=str(group_id),
                sender_id=sender_id,
                sender_username=sender_username)
            kwargs.update(text="———————————————————",
                          reply_markup=markup)
            await send_with_kwargs(bot, session, sender_id, kwargs, message, json_model)

        elif message.text:
            kwargs.update(text=message.html_text+signature)
            await send_with_kwargs(bot, session, sender_id, kwargs, message, json_model)
        
        elif message.caption:
            kwargs.update(caption=message.html_text+signature)
            await send_with_kwargs(bot, session, sender_id, kwargs, message, json_model)
        
        elif message.sticker:
            logger.info("sticker message was blocked")
            await message.answer("Недопустимый тип вложения")
            return
        
        else:
            kwargs.update(caption=signature)
            await send_with_kwargs(bot, session, sender_id, kwargs, message, json_model)
    
    current_ad_message = await db.ads_api.get_ad_message(session)
    text = current_ad_message.html_text if current_ad_message is not None \
        else None 

    if db_bot.is_premium or current_ad_message is None:
        await message.answer(text=messages['ru']['default_ad'])
    elif current_ad_message.photo_link is None:
        await message.answer(text=text)
    else:
        await message.bot.send_photo(
            chat_id=sender_id,
            photo=current_ad_message.photo_link,
            caption=text
        )
    
    await db.ads_api.count_views(session)

