import typing
from typing import List, Dict

from src.models.base import IdCUDMixin
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import (
    String,
    ForeignKey,
    UniqueConstraint,
    JSON,
)


class Dictionary(IdCUDMixin):
    __tablename__ = "dictionary"

    name: Mapped[str] = mapped_column(String(30), comment="Название словаря")
    description: Mapped[str | None] = mapped_column(String(150), comment="Описание")
    topics: Mapped[List["Topic"]] = relationship(back_populates="dictionary")


class Topic(IdCUDMixin):
    __tablename__ = "topic"

    name: Mapped[str] = mapped_column(String(30), comment="Название топика")
    description: Mapped[str | None] = mapped_column(String(150), comment="Описание")
    words: Mapped[List["Words"]] = relationship(back_populates="topic")
    dictionary_id: Mapped[int] = mapped_column(ForeignKey("dictionary.id"))
    dictionary: Mapped["Dictionary"] = relationship(back_populates="topics")
    type_translation: Mapped[str] = mapped_column(
        String(), comment="Тип перевода"
    )  # for example ru-en or en-ru
    tg_user_progress: Mapped[List["TgUserTopicProgress"]] = relationship(
        back_populates="topic"
    )
    trys: Mapped[List["WordTrys"]] = relationship(back_populates="topic")
    battles: Mapped[List["TopicBattles"]] = relationship(back_populates="topic")

    repr_columns = ["id", "name", "type_translation"]


class TgUserTopicProgress(IdCUDMixin):
    __tablename__ = "tg_user_topic_progress"
    __table_args__ = (
        UniqueConstraint(
            "topic_id", "tg_user_id", name="idx_unique_topic_id_tg_user_id"
        ),
    )

    progress: Mapped[int] = mapped_column(
        comment="Прогресс 0-100", default=0, server_default="0"
    )
    tg_user_id: Mapped[int] = mapped_column(ForeignKey("tg_users.tg_id"))
    topic_id: Mapped[int] = mapped_column(ForeignKey("topic.id"))
    topic: Mapped["Topic"] = relationship(back_populates="tg_user_progress")

    repr_columns = ["id", "progress", "tg_user_id"]


class Words(IdCUDMixin):
    __tablename__ = "words"

    topic_id: Mapped[int] = mapped_column(ForeignKey("topic.id"))
    topic: Mapped["Topic"] = relationship(back_populates="words")
    word: Mapped[str] = mapped_column(String(), comment="Слово")
    word_translation: Mapped[str] = mapped_column(String(), comment="Перевод слова")
    trys: Mapped[List["WordTrys"]] = relationship(back_populates="word")

    repr_columns = ["id", "word", "word_translation"]


class WordTrys(IdCUDMixin):
    __tablename__ = "word_trys"
    __table_args__ = (
        UniqueConstraint("word_id", "tg_user_id", name="idx_unique_word_id_tg_user_id"),
    )

    topic_id: Mapped[int] = mapped_column(ForeignKey("topic.id"))
    topic: Mapped["Topic"] = relationship(back_populates="trys")
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id"))
    word: Mapped["Words"] = relationship(back_populates="trys")
    trys: Mapped[int] = mapped_column(
        String(), comment="Попытки", default="❌❌❌❌❌", server_default="❌❌❌❌❌"
    )  # for example ✅❌✅
    tg_user_id: Mapped[int] = mapped_column(ForeignKey("tg_users.tg_id"))

    repr_columns = ["tg_user_id", "word_id", "trys"]


class TopicBattles(IdCUDMixin):
    __tablename__ = "topic_battles"

    topic_id: Mapped[int] = mapped_column(ForeignKey("topic.id"))
    topic: Mapped["Topic"] = relationship(back_populates="battles")
    players: Mapped[Dict] = mapped_column(JSON)
    words: Mapped[List[Dict]] = mapped_column(JSON)
    used_words: Mapped[List[Dict] | None] = mapped_column(JSON)
