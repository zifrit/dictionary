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


async def sed_errors(errors: dict, bot: "Bot", chat_id: int, tg_id: int):
    admin_log_dir = os.path.join(BASE_DIR, "return_user_result")
    if not os.path.exists(admin_log_dir):
        os.makedirs(admin_log_dir)
    save_error_file(errors, f"return_user_result/{tg_id}_error.json")
    file_path = FSInputFile(f"return_user_result/{tg_id}_error.json")
    await bot.send_document(chat_id=chat_id, document=file_path)


async def validate_add_topic(input_dict, bot: "Bot", chat_id: int, tg_id: int) -> bool:
    result = {}
    if not isinstance(input_dict, list):
        result["r"] = "Файл соответствуете шаблону"
        result["error"] = True
        await sed_errors(result, bot, chat_id, tg_id)
        return False

    for item in input_dict:
        result["incorrect_item"] = []
        if (
            not isinstance(item, dict)
            and "word" in item.keys()
            and "translation" in item.keys()
        ):
            result["incorrect_item"].append(item)
            result["message"] = "Эти элементы не правильные"
            result["error"] = True

    if not result["incorrect_item"]:
        await sed_errors(result, bot, chat_id, tg_id)
        return False

    return True


async def parse_json(
    json_data,
    item_data,
    bot: "Bot",
    chat_id: int,
    tg_id: int,
    type_parse: str,
) -> bool | None:

    if type_parse == "create_topic":
        await validate_add_topic(json_data, bot, chat_id, tg_id)
        async with db_session.session_factory() as session:
            topic_schema = CreateTopicSchema(
                name=item_data["name"],
                type_translation=item_data["type_translation"],
                dictionary_id=item_data["dictionary_id"],
            )
            topic = Topic(**topic_schema.model_dump())
            session.add(topic)
            await session.flush()

            words_schema = [
                CreateWordsSchema(
                    topic_id=topic.id,
                    word=word.get("word"),
                    word_translation=word.get("translation"),
                )
                for word in json_data
            ]
            words = [Words(**schema.model_dump()) for schema in words_schema]
            session.add_all(words)
            await session.commit()
            return True
    return None
