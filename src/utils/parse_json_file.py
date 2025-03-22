import json
import os
from typing import TYPE_CHECKING

from src.core.db_connections import db_session
from src.repository.dictionary import dictionary_manager
from src.schemas.dictionary import (
    CreateTopicSchema,
    CreateDictionarySchema,
    CreateWordsSchema,
)
from src.models.dictionary import Dictionary, Topic, Words
from aiogram.types import FSInputFile
from src.core.logger import BASE_DIR

if TYPE_CHECKING:
    from aiogram.client.bot import Bot


def save_error_file(errors: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as file:
        json.dump(errors, file, ensure_ascii=False, indent=4)


async def validate_dict_format(
    input_dict, bot: "Bot", chat_id: int, tg_id: int
) -> bool:
    result = {}

    # Проверяем, что входной параметр является словарем
    if not isinstance(input_dict, dict):
        result["r"] = "Файл пуст"
        result["error"] = True
        save_error_file(result, f"return_user_result/{tg_id}_error.json")
        return result

    # Проверяем наличие всех обязательных ключей
    required_keys = {"words", "dictionary", "topic_name", "type_translation"}
    missing_keys = {
        key: "Обязательное поле" for key in required_keys if key not in input_dict
    }
    if missing_keys:

        result["r"] = missing_keys
        result["error"] = True
        save_error_file(result, f"return_user_result/{tg_id}_error.json")
        return result
    result = {
        "words": [],
        "dictionary": {"name": "", "identification": 0},
        "topic_name": "",
        "type_translation": "",
        "error": False,
    }

    # Проверяем тип "topic_name"
    if not isinstance(input_dict["topic_name"], str):
        result["topic_name"] = "Должен быть строкой"
        result["error"] = True

    # Проверяем тип "type_translation"
    if not isinstance(input_dict["type_translation"], str):
        result["type_translation"] = "Должен быть строкой"
        result["error"] = True

    type_translation = input_dict["type_translation"]
    if len(type_translation.split("-")) > 2 or len(type_translation.split("-")) <= 1:
        result["type_translation"] = "Не верный формат"
        result["error"] = True
    else:
        origin, translate = type_translation.split("-")
        # Проверяем тип "words"
        if not isinstance(input_dict["words"], list):
            result["words"] = "Должен быть списком"
            result["error"] = True
        else:
            for i, item in enumerate(input_dict["words"]):
                if not item.get(origin) and not item.get(translate):
                    result["words"][
                        i
                    ] = "Не соответствует типам слово-перевод из type_translation"
                    result["error"] = True
    # Проверяем "dictionary"
    if not isinstance(input_dict["dictionary"], dict):
        result["dictionary"] = "Не верный формат"
        result["error"] = True
    else:
        if "name" not in input_dict["dictionary"]:
            if "identification" not in input_dict["dictionary"]:
                result["dictionary"] = "в dictionary нету ни названия ни идентификатора"
                result["error"] = True
            elif not isinstance(input_dict["dictionary"]["identification"], int):
                result["dictionary"]["identification"] = "Не верный формат"
                result["error"] = True
            elif isinstance(input_dict["dictionary"]["identification"], int):
                pass
            else:
                result["dictionary"] = "в dictionary нету названия"
                result["error"] = True

        elif not isinstance(input_dict["dictionary"]["name"], str):
            result["dictionary"]["name"] = "Не верный формат"
            result["error"] = True

    if result["error"]:
        admin_log_dir = os.path.join(BASE_DIR, "return_user_result")
        if not os.path.exists(admin_log_dir):
            os.makedirs(admin_log_dir)
        save_error_file(result, f"return_user_result/{tg_id}_error.json")
        file_path = FSInputFile(f"return_user_result/{tg_id}_error.json")
        await bot.send_document(chat_id=chat_id, document=file_path)
        return False

    return True


async def parse_json(json_data, bot: "Bot", chat_id: int, tg_id: int) -> [bool | None]:

    if not await validate_dict_format(json_data, bot, chat_id, tg_id):
        return False

    dictionary_data = json_data.get("dictionary")
    topic_name = json_data.get("topic_name")
    type_translation = json_data.get("type_translation")
    org, trans = type_translation.split("-")
    row_words = json_data.get("words")

    async with db_session.session_factory() as session:
        if dictionary_data.get("identification"):
            dictionary = await dictionary_manager.get_by_id(
                session, dictionary_data.get("identification")
            )
        else:
            dictionary_schema = CreateDictionarySchema(name=dictionary_data.get("name"))
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
        return False
