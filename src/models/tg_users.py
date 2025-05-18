from typing import List

from src.models.base import CUDMixin
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String, BigInteger, Integer


class TgUser(CUDMixin):
    __tablename__ = "tg_users"
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(255))
    chats: Mapped[List[str] | None] = mapped_column(ARRAY(String))
    repr_columns = ["tg_id", "username"]
