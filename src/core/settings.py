from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class BOTSettings(BaseSettings):
    BOT_TOKEN: str


class AdminSettings(BaseSettings):
    SECRET_KEY: str


class Database(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASS: str = "postgres"
    DB_NAME: str = "vpn_market"

    @property
    def database_url_asyncpg(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class RedisSettings(BaseSettings):
    host: str = "localhost"
    port: int = 6379


class Settings(BaseSettings):
    BOT: BOTSettings = BOTSettings()
    REDIS: RedisSettings = RedisSettings()
    ADMIN: AdminSettings = AdminSettings()
    DATABASE: Database = Database()


settings = Settings()

bot = Bot(
    token=settings.BOT.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher(storage=MemoryStorage())
