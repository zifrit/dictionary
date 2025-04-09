from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, load_only, joinedload

from src.repository.base import BaseManager
from src.models import TgUser


class TgUserManager(BaseManager[TgUser]):
    pass


tg_user_manager = TgUserManager(TgUser)
