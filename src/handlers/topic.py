import json
import logging
from contextlib import suppress

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from src.kbs.pagination import Pagination
from src.kbs.topic import about_topic
from src.states.dictionary import SearchTopic, AddTopicToDictionary
from src.repository.dictionary import topic_manager, words_manager
from src.utils.pagination import pagination
from src.utils.parse_json_file import parse_json

loger = logging.getLogger("admin_log")


router = Router()


@router.message(F.text == "/add_topic")
async def add_topic_to_dictionary(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Идентификатор словаря")
    await state.set_state(AddTopicToDictionary.dictionary_id)


@router.message(AddTopicToDictionary.dictionary_id)
async def get_topic_name(message: Message, state: FSMContext):
    text = message.text
    try:
        dictionary_id = int(text)
        await state.update_data(dictionary_id=dictionary_id)
        await state.set_state(AddTopicToDictionary.name)
        await message.reply("Введите название топика. Не больше 30 символов")
    except ValueError:
        await message.reply("Не правильный идентификатор")


@router.message(~F.text, AddTopicToDictionary.name)
async def get_wrong_topic_name(message: Message, state: FSMContext):
    await message.reply("Не правильный тип данных")


@router.message(AddTopicToDictionary.name)
async def get_type_translation_topic(message: Message, state: FSMContext):
    name = message.text
    if len(name) > 30:
        await message.answer("Название слишком длинное")
    else:
        await state.update_data(name=name)
        await state.set_state(AddTopicToDictionary.type_translation)
        await message.answer(
            "Отправьте тип перевода т.е с какого на какой переводятся слова в топике.\nНапример:\n  en-ru (с английского на русский)\n  ru-en (с русского на английский"
        )


@router.message(~F.text, AddTopicToDictionary.type_translation)
async def get_wrong_type_translation_topic(message: Message, state: FSMContext):
    await message.reply("Не правильный тип данных")


@router.message(AddTopicToDictionary.type_translation)
async def get_wrong_type_translation_topic(message: Message, state: FSMContext):
    type_translation = message.text
    await state.update_data(type_translation=type_translation)
    await state.set_state(AddTopicToDictionary.file)
    await message.answer("Отправьте файл со словами и переводами")
    await message.answer(
        """
Вот пример того как долже быть заполнен файл
```json
[
    {
        "word": "Слово которое хотите учить",
        "translation": "Перевод слова",
    },
    {
        "word": "Слово которое хотите учить",
        "translation": "Перевод слова",
    },

    ...
]
```
""",
        parse_mode="Markdown",
    )


@router.message(~F.document, AddTopicToDictionary.file)
async def get_wrong_topic_document(message: Message):
    await message.reply("Это не файл")


@router.message(AddTopicToDictionary.file)
async def get_topic_document(message: Message, state: FSMContext):
    file_name = message.document.file_name
    if len(file_name.split(".")) > 2 and file_name.split(".")[-1] != "json":
        await message.reply("Не верный формат файла")
    else:
        file_id = message.document.file_id
        file = await message.bot.get_file(file_id)
        file_path = file.file_path
        downloaded_file = await message.bot.download_file(file_path)
        try:
            json_data = json.loads(downloaded_file.read().decode("utf-8"))
        except json.decoder.JSONDecodeError:
            await message.reply("В файле ошибка убедитесь что он соответствует шаблону")
        else:
            data = state.get_data()
            if await parse_json(
                json_data,
                bot=message.bot,
                chat_id=message.chat.id,
                tg_id=message.from_user.id,
                type_parse="create_topic",
                item_data=data,
            ):
                await message.reply("Проблема с данными")
            else:
                await message.reply("Данные успешно сохранились")
                await state.clear()


@router.message(F.text == "/search_topic")
async def search_topic(message: Message, state: FSMContext):
    await message.answer("Введите идентификатор словаря")
    await state.clear()
    await state.set_state(SearchTopic.topic_id)


@router.message(~F.text, SearchTopic.topic_id)
async def get_wrong_topic_id(message: Message):
    await message.reply("Не верный формат ввода")


@router.message(SearchTopic.topic_id)
async def get_bio_topic_type_1(
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
        title_key="name",
        item_callback_data="topic",
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
        title_key="name",
        item_callback_data="topic",
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


@router.callback_query(F.data.startswith("topic_"))
async def get_bio_topic_type_2(call: CallbackQuery, db_session: AsyncSession):
    topic_id = int(call.data.split("_")[-1])
    topic = await topic_manager.get_by_id(db_session, id_=topic_id)
    user_progress = await topic_manager.get_tg_user_progress(
        db_session, topic_id=topic_id, tg_id=call.from_user.id
    )
    if topic:
        text = f"""
Название: {topic.name}
Идентификатор: {topic.id}
Количество слов: {len(topic.words)}
Перевод: {topic.type_translation}
Описание: {topic.description}
Прогресс: {user_progress.progress if user_progress else 0}%
                        """
        await call.message.edit_text(text=text, reply_markup=about_topic(topic_id))


@router.callback_query(F.data.startswith("reset_topic_progress_"))
async def reset_topic_progress(call: CallbackQuery, db_session: AsyncSession):
    topic_id = int(call.data.split("_")[-1])
    await topic_manager.reset_tg_user_progres(
        db_session, topic_id=topic_id, tg_id=call.from_user.id
    )

    topic = await topic_manager.get_by_id(db_session, id_=topic_id)
    user_progress = await topic_manager.get_tg_user_progress(
        db_session, topic_id=topic_id, tg_id=call.from_user.id
    )
    if topic:
        text = f"""
Название: {topic.name}
Идентификатор: {topic.id}
Количество слов: {len(topic.words)}
Перевод: {topic.type_translation}
Описание: {topic.description}
Прогресс: {user_progress.progress if user_progress else 0}%
                            """

        await call.message.delete()
        await call.message.answer(text=text, reply_markup=about_topic(topic_id))
