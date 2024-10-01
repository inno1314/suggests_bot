from aiogram.fsm.state import StatesGroup, State


class BotSettings(StatesGroup):
    change = State()
    formatting = State()

