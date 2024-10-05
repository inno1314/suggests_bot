from aiogram.fsm.state import StatesGroup, State


class PublishMedia(StatesGroup):
    messages = State()
