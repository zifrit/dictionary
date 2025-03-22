from src.schemas.base import BaseSchema


class DictionarySchema(BaseSchema):
    name: str


class CreateDictionarySchema(DictionarySchema):
    pass


class TopicSchema(BaseSchema):
    pass


class CreateTopicSchema(TopicSchema):
    name: str
    type_translation: str
    dictionary_id: int


class WordsSchema(BaseSchema):
    pass


class CreateWordsSchema(WordsSchema):
    topic_id: int
    word: str
    word_translation: str
