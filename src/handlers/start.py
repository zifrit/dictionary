import logging
from aiogram import Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from src.repository.tg_user import tg_user_manager
from src.schemas.tg_user import CreateTgUserSchema

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
    if tg_user_manager.get_by_id(db_session, id_=message.from_user.id) is None:
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
