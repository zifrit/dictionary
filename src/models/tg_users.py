from src.models.base import CUDMixin
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, BigInteger


class TgUser(CUDMixin):
    __tablename__ = "tg_users"
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(255))

    repr_columns = ["tg_id", "username"]
