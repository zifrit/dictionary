from aiogram.fsm.state import StatesGroup, State


class AddTopicToDictionary(StatesGroup):
    dictionary_id = State()
    file = State()
    type_translation = State()
    name = State()


class CreateNewDictionary(StatesGroup):
    name = State()


class SearchDictionary(StatesGroup):
    dictionary_id = State()


class SearchTopic(StatesGroup):
    topic_id = State()
