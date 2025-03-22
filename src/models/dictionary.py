from typing import List

from src.models.base import IdCUDMixin
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, ForeignKey, DateTime, Integer, Text, Boolean


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
    progress: Mapped[int] = mapped_column(
        comment="Прогресс 0-100", default=0, server_default="0"
    )

    repr_columns = ["id", "name", "type_translation"]


class Words(IdCUDMixin):
    __tablename__ = "words"

    topic_id: Mapped[int] = mapped_column(ForeignKey("topic.id"))
    topic: Mapped["Topic"] = relationship(back_populates="words")
    word: Mapped[str] = mapped_column(String(), comment="Слово")
    word_translation: Mapped[str] = mapped_column(String(), comment="Перевод слова")
    trys: Mapped[int] = mapped_column(
        String(), comment="Попытки", default="❌❌❌❌❌", server_default="❌❌❌❌❌"
    )  # for example ✅❌✅

    repr_columns = ["id", "word", "word_translation"]
