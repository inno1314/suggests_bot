from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from states import BotSettings
from keyboards.inline import make_formatting_markup
from data.messages import messages

router = Router()

@router.callback_query(BotSettings.change, F.data == "formats")
async def bot_formatting(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    bot_id = int(data.get('bot_id'))
    markup = await make_formatting_markup(bot_id)
    await call.message.edit_text(messages['ru']['bot_formatting'],
                                 reply_markup=markup)

