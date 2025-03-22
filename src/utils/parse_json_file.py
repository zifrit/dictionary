import json
from src.core.db_connections import db_session
from src.schemas.dictionary import (
    CreateTopicSchema,
    CreateDictionarySchema,
    CreateWordsSchema,
)
from src.models.dictionary import Dictionary, Topic, Words


async def parse_json(json_data, file_name) -> [str | None]:
    errors = []
    if json_data is None:
        errors.append(f"Файл {file_name} пустой")
        return "\n".join(errors)

    if not isinstance(json_data, dict):
        errors.append(f"Файл {file_name} имеет не верный формат")
        return "\n".join(errors)

    if not json_data.get("dictionary_name"):
        errors.append("В файле отсутствует ключ dictionary_name")

    if not json_data.get("topic_name"):
        errors.append("В файле отсутствует ключ topic_name")

    if not json_data.get("type_translation"):
        errors.append("В файле отсутствует ключ type_translation")

    if not json_data.get("words"):
        errors.append("В файле отсутствует ключ words")

    else:
        dictionary_name = json_data.get("dictionary_name")
        topic_name = json_data.get("topic_name")
        type_translation = json_data.get("type_translation")
        org, trans = type_translation.split("-")
        row_words = json_data.get("words")
        check_words = all(
            [
                all([word.get(org) is not None, word.get(trans) is not None])
                for word in row_words
            ]
        )

        if not check_words:
            errors.append("Не правильны формат данных в words")
            return "\n".join(errors)

        async with db_session.session_factory() as session:

            dictionary_schema = CreateDictionarySchema(name=dictionary_name)
            dictionary = Dictionary(**dictionary_schema.model_dump())
            session.add(dictionary)
            await session.flush()

            topic_schema = CreateTopicSchema(
                name=topic_name,
                type_translation=type_translation,
                dictionary_id=dictionary.id,
            )
            topic = Topic(**topic_schema.model_dump())
            session.add(topic)
            await session.flush()

            words_schema = [
                CreateWordsSchema(
                    topic_id=topic.id,
                    word=word.get(org),
                    word_translation=word.get(trans),
                )
                for word in row_words
            ]
            words = [Words(**schema.model_dump()) for schema in words_schema]
            session.add_all(words)
            await session.commit()

    if errors:
        return "\n".join(errors)
