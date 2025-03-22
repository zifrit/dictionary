from aiogram.fsm.state import StatesGroup, State


class AddDictionary(StatesGroup):
    file = State()


class SearchDictionary(StatesGroup):
    dictionary_id = State()


class SearchTopic(StatesGroup):
    dictionary_id = State()
