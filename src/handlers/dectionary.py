import json
import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from src.states.dictionary import AddDictionary
from src.utils.parse_json_file import parse_json

from src.kbs.other import move_to

loger = logging.getLogger("admin_log")


router = Router()


@router.message(F.text == "/add_topic")
async def add_dictionary(message: Message, state: FSMContext):
    await message.answer("Отправьте json файл")
    await state.set_state(AddDictionary.file)


@router.message(~F.document, AddDictionary.file)
async def process_image_invalid(message: Message):
    await message.reply("Это не файл")


@router.message(AddDictionary.file)
async def get_image_user(message: Message, state: FSMContext):
    file_name = message.document.file_name
    if len(file_name.split(".")) > 2 and file_name.split(".")[-1] != "json":
        await message.reply("Не верный формат файла")
    else:
        file_id = message.document.file_id
        file = await message.bot.get_file(file_id)
        file_path = file.file_path
        downloaded_file = await message.bot.download_file(file_path)
        json_data = json.loads(downloaded_file.read().decode("utf-8"))
        if result := await parse_json(json_data, file_name):
            await message.reply(text=result)
        else:
            await message.reply("Данные успешно сохранились")
            await state.set_state(AddDictionary.file)
            await state.clear()


