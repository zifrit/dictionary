from typing import Any, Coroutine

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.repository.base import BaseManager
from src.models import Dictionary, Topic, Words


class DictionaryManager(BaseManager[Dictionary]):
    async def get_by_id(
        self, session: AsyncSession, id_: int, *args, **kwargs
    ) -> Dictionary:
        result = await session.scalar(
            select(self._model)
            .options(selectinload(Dictionary.topics).load_only(Topic.id))
            .where(
                self._model.id == id_,
                self._model.deleted_at.is_(None),
            )
        )
        return result

    async def get_all(self, session: AsyncSession) -> list[Dictionary]:
        result = await session.scalars(
            select(self._model)
            .options(selectinload(Dictionary.topics).load_only(Topic.id))
            .where(
                self._model.deleted_at.is_(None),
            )
        )
        return list(result)

    async def count(self, session: AsyncSession) -> int:
        count_obj = await session.execute(select(func.count(self._model.id)))
        count_obj = count_obj.scalar_one()
        return count_obj

    async def get_pagination(
        self,
        session: AsyncSession,
        limit: int = 5,  # page size
        offset: int = 1,  # page number
    ) -> tuple[list[Dictionary], int]:
        result = await session.scalars(
            select(self._model)
            .limit(limit)
            .offset(offset=(limit * (offset - 1)))
            .options(selectinload(Dictionary.topics).load_only(Topic.id))
            .where(
                self._model.deleted_at.is_(None),
            )
        )
        return list(result), await self.count(session)


class TopicManager(BaseManager[Topic]):

    async def get_all_by_dictionary_id(
        self, session: AsyncSession, dictionary_id: int
    ) -> list[Topic]:
        result = await session.scalars(
            select(self._model)
            .options(selectinload(Topic.words).load_only(Words.id))
            .where(
                self._model.dictionary_id == dictionary_id,
                self._model.deleted_at.is_(None),
            )
        )
        return list(result)

    async def get_by_id(
        self, session: AsyncSession, id_: int, *args, **kwargs
    ) -> Topic:
        result = await session.scalar(
            select(self._model)
            .options(selectinload(Topic.words).load_only(Words.id))
            .where(
                self._model.id == id_,
                self._model.deleted_at.is_(None),
            )
        )
        return result

    async def count(self, session: AsyncSession, dictionary_id: int) -> int:
        count_obj = await session.execute(
            select(func.count(self._model.id)).where(
                self._model.dictionary_id == dictionary_id,
            )
        )
        count_obj = count_obj.scalar_one()
        return count_obj

    async def get_pagination(
        self,
        session: AsyncSession,
        dictionary_id: int,
        limit: int = 5,  # page size
        offset: int = 1,  # page number
    ) -> tuple[list[Topic], int]:
        result = await session.scalars(
            select(self._model)
            .limit(limit)
            .offset(offset=(limit * (offset - 1)))
            .options(selectinload(Topic.words).load_only(Words.id))
            .where(
                self._model.dictionary_id == dictionary_id,
                self._model.deleted_at.is_(None),
            )
        )
        return list(result), await self.count(session, dictionary_id)


class WordsManager(BaseManager[Words]):
    pass


dictionary_manager = DictionaryManager(Dictionary)
topic_manager = TopicManager(Topic)
words_manager = WordsManager(Words)
