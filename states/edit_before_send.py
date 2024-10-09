from aiogram.fsm.state import StatesGroup, State


class EditBeforeSend(StatesGroup):
    editing = State()
    sending = State()
