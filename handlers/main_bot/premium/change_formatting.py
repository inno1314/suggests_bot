import logging
from aiogram import html, types, Router, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from database.model import Bot
from data.config import db
from states import BotSettings
from keyboards.inline import formatting_markup, make_formatting_markup, ok_button
from data.messages import messages

logger = logging.getLogger(__name__)
default_texts = {
    "start_msg_formatting": messages["senders_start"],
    "answer_msg_formatting": messages["default_answer"],
    "post_formatting": "<i>Не установлена</i>",
}
texts_for_admin = {
    "start_msg_formatting": messages["start_msg_formatting"],
    "answer_msg_formatting": messages["answer_msg_formatting"],
    "post_formatting": messages["post_formatting"],
}
db_fields = {
    "start_msg_formatting": "start_message",
    "answer_msg_formatting": "answer_message",
    "post_formatting": "post_formatting",
}

router = Router()


async def get_current_message(formatting_field: str, db_bot: Bot):
    if formatting_field == "start_msg_formatting":
        text = db_bot.start_message
    elif formatting_field == "answer_msg_formatting":
        text = db_bot.answer_message
    else:
        text = db_bot.post_formatting

    return text if text is not None else default_texts[formatting_field]


@router.callback_query(BotSettings.change, F.data == "formats")
async def bot_formatting(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    bot_id = int(data.get("bot_id"))
    markup = await make_formatting_markup(bot_id)
    await call.message.edit_text(messages["bot_formatting"], reply_markup=markup)


@router.callback_query(
    BotSettings.change,
    F.data.in_(["start_msg_formatting", "answer_msg_formatting", "post_formatting"]),
)
async def post_formatting(
    call: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    formatting_field: str = call.data
    data = await state.get_data()
    bot_id = int(data.get("bot_id"))
    db_bot = await db.bot_api.get_bot(session, bot_id)
    current_formatting = await get_current_message(formatting_field, db_bot)
    text = texts_for_admin[formatting_field] + current_formatting

    await state.set_state(BotSettings.formatting)
    await state.update_data(message_id=call.message.message_id)
    await state.update_data(formatting_field=formatting_field)

    markup = await formatting_markup(formatting_field, bot_id)
    await call.message.edit_text(text, reply_markup=markup)


@router.callback_query(
    BotSettings.formatting,
    F.data.in_(
        [
            "clear_start_msg_formatting",
            "clear_answer_msg_formatting",
            "clear_post_formatting",
        ]
    ),
)
async def delete_formatting(
    call: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    data = await state.get_data()
    bot_id = int(data.get("bot_id"))
    formatting_field = call.data[6:]

    await db.bot_api.update_bot_field(
        session, bot_id, db_fields[formatting_field], None
    )
    text = texts_for_admin[formatting_field] + default_texts[formatting_field]

    markup = await formatting_markup(formatting_field, bot_id)
    await call.message.edit_text(text, reply_markup=markup)


@router.message(BotSettings.formatting, F.text)
async def set_new_formatting(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    bot = message.bot
    new_formatting = message.html_text
    data = await state.get_data()
    bot_id = int(data.get("bot_id"))
    formatting_field: str = data.get("formatting_field")

    await message.delete()
    try:
        await db.bot_api.update_bot_field(
            session, bot_id, db_fields[formatting_field], new_formatting
        )
    except Exception as e:
        logger.info(f"Error while changing post_formatting: {e}")
        return await message.answer(
            f"{html.bold('❗️Не удалось добавить ваше сообщение!')}",
            reply_markup=ok_button,
        )

    message_id = int(data.get("message_id"))
    text = texts_for_admin[formatting_field] + new_formatting
    markup = await formatting_markup(formatting_field, bot_id)
    await bot.edit_message_text(
        text, message.from_user.id, message_id, reply_markup=markup
    )


@router.message(BotSettings.formatting)
async def set_new_formatting(message: types.Message):
    await message.delete()
