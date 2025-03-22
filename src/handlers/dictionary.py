import json
import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest

from src.kbs.pagination import Pagination
from src.states.dictionary import AddDictionary, SearchDictionary, SearchTopic
from src.repository.dictionary import dictionary_manager, topic_manager
from src.utils.parse_json_file import parse_json
from src.kbs.dictionary import about_dictionary
from src.utils.pagination import pagination
from src.kbs.other import move_to

loger = logging.getLogger("admin_log")


router = Router()


@router.message(F.text == "/add_topic")
async def add_dictionary(message: Message, state: FSMContext):
    await message.answer("Отправьте json файл")
    await state.set_state(AddDictionary.file)


@router.message(~F.document, AddDictionary.file)
async def get_wrong_document(message: Message):
    await message.reply("Это не файл")


@router.message(AddDictionary.file)
async def get_right_document(message: Message, state: FSMContext):
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
            await message.reply("В файле ошибка убедитесь что он соответсвуте шаблону")
        else:
            if not await parse_json(
                json_data,
                bot=message.bot,
                chat_id=message.chat.id,
                tg_id=message.from_user.id,
            ):
                ...
            else:
                await message.reply("Данные успешно сохранились")
                await state.clear()


@router.message(F.text == "/list_dictionary")
async def list_dictionary(message: Message, db_session: AsyncSession):
    text, reply_markup = await pagination(
        session=db_session,
        count_data_in_page=3,
        model_manage=dictionary_manager,
        nex_action_text="next_page_dictionary",
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
        callback_data=callback_data,
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
    await message.answer("Введите идентификатор словаря")
    await state.set_state(SearchDictionary.dictionary_id)


@router.message(~F.text, SearchDictionary.dictionary_id)
async def get_wrong_dictionary_id(message: Message):
    await message.reply("Не верный формат ввода")


@router.message(SearchDictionary.dictionary_id)
async def get_right_dictionary_id(
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
