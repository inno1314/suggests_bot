from aiogram.fsm.state import StatesGroup, State


class AddingBot(StatesGroup):
    token = State()
