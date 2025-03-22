from src.repository.base import BaseManager
from src.models import Dictionary, Topic, Words


class DictionaryManager(BaseManager[Dictionary]):
    pass


class TopicManager(BaseManager[Topic]):
    pass


class WordsManager(BaseManager[Words]):
    pass


dictionary_manager = DictionaryManager(Dictionary)
topic_manager = TopicManager(Topic)
words_manager = WordsManager(Words)
