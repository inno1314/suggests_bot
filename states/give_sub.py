from aiogram.fsm.state import StatesGroup, State


class GiveSub(StatesGroup):
    choosing_option = State()
    getting_id = State()
