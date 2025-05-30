import json
import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest

from src.kbs.pagination import Pagination
from src.states.dictionary import SearchDictionary, CreateNewDictionary
from src.repository.dictionary import dictionary_manager
from src.kbs.dictionary import about_dictionary
from src.utils.pagination import pagination

loger = logging.getLogger("admin_log")


router = Router()


@router.message(F.text == "/new_dictionary")
async def new_dictionary(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Какое название словаря хотите ?")
    await state.set_state(CreateNewDictionary.name)


@router.message(CreateNewDictionary.name)
async def get_topic_name(message: Message, state: FSMContext):
    name = message.text
    await message.reply("Введите название топика. Не больше 30 символов")


@router.message(F.text == "/list_dictionary")
async def list_dictionary(message: Message, db_session: AsyncSession, state: FSMContext):
    await state.clear()
    text, reply_markup = await pagination(
        session=db_session,
        count_data_in_page=3,
        model_manage=dictionary_manager,
        nex_action_text="next_page_dictionary",
        title_key="name",
        item_callback_data="dictionary",
        fields={
            "name": "Название",
            "id": "Идентификатор",
            "description": "Описание",
            "topics": {"action": "len", "topics": "Количество топиков"},
        },
    )
    with suppress(TelegramBadRequest):
        await message.answer(text, reply_markup=reply_markup)


@router.callback_query(
    Pagination.filter(F.action.in_(["prev_page_dictionary", "next_page_dictionary"]))
)
async def paginator_dictionary(
    call: CallbackQuery, callback_data: Pagination, db_session: AsyncSession
):
    text, reply_markup = await pagination(
        session=db_session,
        count_data_in_page=3,
        model_manage=dictionary_manager,
        nex_action_text="next_page_dictionary",
        prev_action_text="prev_page_dictionary",
        pagination_callback_data=callback_data,
        title_key="name",
        item_callback_data="dictionary",
        start=False,
        fields={
            "name": "Название",
            "id": "Идентификатор",
            "description": "Описание",
            "topics": {"action": "len", "topics": "Количество топиков"},
        },
    )
    with suppress(TelegramBadRequest):
        await call.message.edit_text(text, reply_markup=reply_markup)


@router.message(F.text == "/search_dictionary")
async def search_dictionary(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Введите идентификатор словаря")
    await state.set_state(SearchDictionary.dictionary_id)


@router.message(~F.text, SearchDictionary.dictionary_id)
async def get_wrong_dictionary_id(message: Message):
    await message.reply("Не верный формат ввода")


@router.message(SearchDictionary.dictionary_id)
async def get_dictionary_bio_type_1(
    message: Message, db_session: AsyncSession, state: FSMContext
):
    message_text = message.text
    try:
        dictionary_id = int(message_text)
        await state.update_data(dictionary_id=dictionary_id)
    except ValueError:
        await message.reply("Идентификатор должен быть числом")
    else:
        dictionary = await dictionary_manager.get_by_id(db_session, id_=dictionary_id)
        text = f"""
Название: {dictionary.name}
Описание: {dictionary.description}
Количество топиков: {len(dictionary.topics)}
        """
        await message.reply(text=text, reply_markup=about_dictionary)


@router.callback_query(F.data.startswith("dictionary_"))
async def get_dictionary_bio_type_2(
    call: CallbackQuery, db_session: AsyncSession, state: FSMContext
):
    dictionary_id = int(call.data.split("_")[-1])
    dictionary = await dictionary_manager.get_by_id(db_session, id_=dictionary_id)
    await state.update_data(dictionary_id=dictionary_id)
    text = f"""
Название: {dictionary.name}
Описание: {dictionary.description}
Количество топиков: {len(dictionary.topics)}
            """
    await call.message.edit_text(text=text, reply_markup=about_dictionary)
