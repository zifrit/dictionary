from src.schemas.base import BaseSchema


class BaseTgUserSchema(BaseSchema):
    tg_id: int
    username: str


class CreateTgUserSchema(BaseTgUserSchema):
    username: str | None = None


class CreateFromChatTgUserSchema(BaseTgUserSchema):
    username: str | None = None
    chats: list[int]
