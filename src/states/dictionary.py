from aiogram.fsm.state import StatesGroup, State


class AddDictionary(StatesGroup):
    file = State()
