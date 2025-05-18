import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from src.repository.tg_user import tg_user_manager
from src.schemas.tg_user import CreateTgUserSchema, CreateFromChatTgUserSchema

loger = logging.getLogger("admin_log")


router = Router()


@router.message(CommandStart())
async def start_handler(
    message: Message, command: CommandObject, db_session: AsyncSession
):
    tg_user_create_schema = CreateTgUserSchema(
        tg_id=message.from_user.id,
        username=message.from_user.username,
    )
    if await tg_user_manager.get_by_id(db_session, id_=message.from_user.id) is None:
        await tg_user_manager.create(
            session=db_session, obj_schema=tg_user_create_schema
        )
    await message.answer(
        """
Доступные команды:
/add_topic
/list_dictionary
/search_dictionary
/search_topic

        """,
    )


@router.message(F.text == "/add_me")
async def add_tg_user_chat(message: Message, db_session: AsyncSession):
    if message.chat.id == message.from_user.id:
        await message.reply("Эта команда не доступна в личном чате")
    else:
        if not await tg_user_manager.is_exist(db_session, tg_id=message.from_user.id):
            tg_user_create_schema = CreateTgUserSchema(
                tg_id=message.from_user.id,
                username=message.from_user.username,
            )
            await tg_user_manager.create(
                session=db_session, obj_schema=tg_user_create_schema
            )
        if await tg_user_manager.check_chat(
            db_session, chat_id=message.chat.id, tg_id=message.from_user.id
        ):
            await message.reply("Вы уже добавлены")
        else:
            await tg_user_manager.add_tg_user_chat(
                session=db_session, tg_id=message.from_user.id, chat_id=message.chat.id
            )
            await message.reply("Вы были добавлены")
