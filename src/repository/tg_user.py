from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, load_only, joinedload

from src.repository.base import BaseManager
from src.models import TgUser


class TgUserManager(BaseManager[TgUser]):
    async def get_by_id(
        self, session: AsyncSession, id_: int, *args, **kwargs
    ) -> TgUser:
        result = await session.scalar(
            select(self._model).where(
                self._model.tg_id == id_,
                self._model.deleted_at.is_(None),
            )
        )
        return result

    async def add_tg_user_chat(
        self, session: AsyncSession, chat_id: int, tg_id: int
    ) -> None:
        tg_user = await session.scalar(select(self._model).where(TgUser.tg_id == tg_id))
        if not tg_user.chats:
            tg_user.chats = [str(chat_id)]
        else:
            tg_user.chats = [str(chat_id)] + tg_user.chats

    async def check_chat(self, session: AsyncSession, chat_id: int, tg_id: int) -> bool:
        tg_user = await session.scalar(
            select(self._model).where(
                TgUser.tg_id == tg_id,
            )
        )
        return tg_user.chats and str(chat_id) in tg_user.chats

    async def is_exist(self, session: AsyncSession, tg_id: int) -> bool:
        result = await session.scalars(select(self._model).where(TgUser.tg_id == tg_id))
        if result.first():
            return True
        return False


tg_user_manager = TgUserManager(TgUser)
