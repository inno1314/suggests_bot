from aiogram.fsm.state import StatesGroup, State


class TopUpBalance(StatesGroup):
    balance = State()
