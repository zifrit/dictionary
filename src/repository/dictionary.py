from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, load_only, joinedload

from src.repository.base import BaseManager
from src.models import (
    Dictionary,
    Topic,
    Words,
    WordTrys,
    TgUserTopicProgress,
    TopicBattles,
    TgUser,
)


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

    @staticmethod
    async def get_tg_user_progress(
        session: AsyncSession, topic_id: int, tg_id: int
    ) -> TgUserTopicProgress:
        result = await session.scalar(
            select(TgUserTopicProgress).where(
                TgUserTopicProgress.topic_id == topic_id,
                TgUserTopicProgress.tg_user_id == tg_id,
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

    async def get_random_topic(self, session: AsyncSession) -> Topic:
        return await session.scalar(select(self._model).order_by(func.random()))

    @staticmethod
    async def start_battle(
        session: AsyncSession,
        chat_id: int,
        topic_id: int | None = None,
        players: list[str] | None = None,
    ) -> TopicBattles:

        if not topic_id:
            topic = await topic_manager.get_random_topic(session)
            topic_id = topic.id
        if not players:
            tg_users = await session.scalars(
                select(TgUser).where(TgUser.chats.contains([str(chat_id)]))
            )
            players = {tg_user.tg_id: 0 for tg_user in tg_users}
        else:
            tg_users = await session.scalars(
                select(TgUser).where(
                    TgUser.username.in_(players),
                    TgUser.chats.contains([str(chat_id)]),
                )
            )
            players = {tg_user.tg_id: 0 for tg_user in tg_users}
        rwo_words = await session.scalars(
            select(Words).where(Words.topic_id == topic_id)
        )
        words = [
            {"word": word.word, "translate": word.word_translation}
            for word in rwo_words
        ]
        battle = TopicBattles(
            topic_id=topic_id,
            players=players,
            words=words,
        )
        session.add(battle)
        await session.commit()
        return battle

    @staticmethod
    async def get_battle(session: AsyncSession, battle_id: int) -> TopicBattles:
        return await session.scalar(
            select(TopicBattles).where(TopicBattles.id == battle_id)
        )

    async def check_started(
        self, session: AsyncSession, topic_id: int, tg_id: int
    ) -> None:
        random_word_trys = await session.scalar(
            select(WordTrys)
            .where(WordTrys.topic_id == topic_id, WordTrys.tg_user_id == tg_id)
            .order_by(func.random())
        )
        if not random_word_trys:
            topic = await self.get_by_id(session, topic_id)
            topic_words = topic.words
            session.add_all(
                [
                    WordTrys(
                        word_id=word.id,
                        tg_user_id=tg_id,
                        topic_id=topic.id,
                    )
                    for word in topic_words
                ]
            )
            session.add(TgUserTopicProgress(topic_id=topic_id, tg_user_id=tg_id))
            await session.commit()


class WordsManager(BaseManager[Words]):
    async def get_random_three_words(self, session: AsyncSession) -> list[Words]:
        result = await session.scalars(
            select(self._model).order_by(func.random()).limit(3)
        )
        return list(result)

    async def get_random_word_trys(
        self,
        session: AsyncSession,
        topic_id: int,
        tg_id: int,
    ) -> WordTrys:
        random_word = await session.scalar(
            select(self._model)
            .where(self._model.topic_id == topic_id)
            .order_by(func.random())
        )
        word_trys = await session.scalar(
            select(WordTrys)
            .options(
                joinedload(WordTrys.word).load_only(Words.word, Words.word_translation)
            )
            .where(WordTrys.word_id == random_word.id, WordTrys.tg_user_id == tg_id)
        )
        return word_trys

    @staticmethod
    async def check_result(session: AsyncSession, topic_id: int, tg_id: int) -> int:
        count_right = await session.execute(
            select(func.count(WordTrys.id)).where(
                WordTrys.trys == "✅✅✅✅✅",
                WordTrys.topic_id == topic_id,
                WordTrys.tg_user_id == tg_id,
            )
        )
        count_right = count_right.scalar_one()

        count_all = await session.execute(
            select(func.count(WordTrys.id)).where(
                WordTrys.topic_id == topic_id,
                WordTrys.tg_user_id == tg_id,
            )
        )
        count_all = count_all.scalar_one()
        progress = int(count_right / count_all * 100)
        return progress

    @staticmethod
    async def get_trys(session: AsyncSession, id_: int) -> WordTrys:
        return await session.scalar(
            select(WordTrys)
            .options(
                joinedload(WordTrys.word).load_only(Words.word, Words.word_translation)
            )
            .where(WordTrys.id == id_)
        )


dictionary_manager = DictionaryManager(Dictionary)
topic_manager = TopicManager(Topic)
words_manager = WordsManager(Words)
