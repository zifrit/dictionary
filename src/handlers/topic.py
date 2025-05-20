import logging
from contextlib import suppress

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from src.kbs.pagination import Pagination
from src.kbs.topic import about_topic
from src.states.dictionary import SearchTopic
from src.repository.dictionary import topic_manager, words_manager
from src.utils.pagination import pagination

loger = logging.getLogger("admin_log")


router = Router()


@router.message(F.text == "/search_topic")
async def search_topic(message: Message, state: FSMContext):
    await message.answer("Введите идентификатор словаря")
    await state.clear()
    await state.set_state(SearchTopic.topic_id)


@router.message(~F.text, SearchTopic.topic_id)
async def get_wrong_topic_id(message: Message):
    await message.reply("Не верный формат ввода")


@router.message(SearchTopic.topic_id)
async def get_right_topic_id(
    message: Message, db_session: AsyncSession, state: FSMContext
):
    message_text = message.text
    try:
        topic_id = int(message_text)
        topic = await topic_manager.get_by_id(db_session, id_=topic_id)
        user_progress = await topic_manager.get_tg_user_progress(
            db_session, topic_id=topic_id, tg_id=message.from_user.id
        )
        if topic:
            await state.update_data(topic_id=topic_id)
            text = f"""
Название: {topic.name}
Идентификатор: {topic.id}
Количество слов: {len(topic.words)}
Перевод: {topic.type_translation}
Описание: {topic.description}
Прогресс: {user_progress.progress if user_progress else 0}%
                    """
            await message.reply(text=text, reply_markup=about_topic(topic_id))
        else:
            await message.reply("Топик с таким идентификатором не найден")
    except ValueError:
        await message.reply("Идентификатор должен быть числом")


@router.callback_query(F.data == "list_topics")
async def list_topics(call: CallbackQuery, state: FSMContext, db_session: AsyncSession):
    state_date = await state.get_data()
    await state.clear()
    dictionary_id = state_date.get("dictionary_id")
    text, reply_markup = await pagination(
        session=db_session,
        count_data_in_page=3,
        model_manage=topic_manager,
        filters={"dictionary_id": dictionary_id},
        nex_action_text="next_page_topic",
        fields={
            "name": "Название",
            "id": "Идентификатор",
            "words": {"action": "len", "words": "Количество слов"},
            "type_translation": "Перевод",
            "description": "Описание",
        },
    )
    with suppress(TelegramBadRequest):
        await call.message.answer(text, reply_markup=reply_markup)


@router.callback_query(
    Pagination.filter(F.action.in_(["prev_page_topic", "next_page_topic"]))
)
async def paginator_topics(
    call: CallbackQuery,
    callback_data: Pagination,
    db_session: AsyncSession,
    state: FSMContext,
):
    state_date = await state.get_data()
    dictionary_id = state_date.get("dictionary_id")
    text, reply_markup = await pagination(
        session=db_session,
        count_data_in_page=3,
        model_manage=topic_manager,
        filters={"dictionary_id": dictionary_id},
        nex_action_text="next_page_topic",
        prev_action_text="prev_page_topic",
        pagination_callback_data=callback_data,
        start=False,
        fields={
            "name": "Название",
            "id": "Идентификатор",
            "words": {"action": "len", "words": "Количество слов"},
            "type_translation": "Перевод",
            "description": "Описание",
        },
    )
    with suppress(TelegramBadRequest):
        await call.message.edit_text(text, reply_markup=reply_markup)


@router.callback_query(F.data.startswith("back_to_topic_"))
async def back_to_topic(call: CallbackQuery, db_session: AsyncSession):
    topic_id = call.data.split("_")[-1]
    topic = await topic_manager.get_by_id(db_session, id_=int(topic_id))
    progress = await words_manager.check_result(
        session=db_session, topic_id=int(topic_id), tg_id=call.from_user.id
    )
    tg_user_progress = await topic_manager.get_tg_user_progress(
        db_session, topic_id=int(topic_id), tg_id=call.from_user.id
    )
    topic.progress = progress

    text = f"""
Название: {topic.name}
Идентификатор: {topic.id}
Количество слов: {len(topic.words)}
Перевод: {topic.type_translation}
Описание: {topic.description}
Прогресс: {tg_user_progress.progress} %
            """
    await call.message.edit_text(text=text, reply_markup=about_topic(int(topic_id)))
