import json
import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from src.states.dictionary import AddDictionary, SearchDictionary, SearchTopic
from src.repository.dictionary import dictionary_manager, topic_manager
from src.utils.parse_json_file import parse_json
from src.kbs.dictionary import about_dictionary
from src.kbs.other import move_to

loger = logging.getLogger("admin_log")


router = Router()


@router.callback_query(F.data == "list_topics")
async def list_topics(
    callback: CallbackQuery, state: FSMContext, db_session: AsyncSession
):
    state_date = await state.get_data()
    dictionary_id = state_date.get("dictionary_id")
    topics = await topic_manager.get_all_by_dictionary_id(db_session, dictionary_id)
    text = [
        f"""
Название: {topic.name}
Идентификатор: {topic.id}
Количество слов: {len(topic.words)}
Перевод: {topic.type_translation}
Описание: {topic.description}
"""
        for topic in topics
    ]
    await callback.message.edit_text(
        text="\n\n".join(text),
    )
