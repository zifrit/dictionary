import asyncio
import logging.config
from aiogram import types

from src.core.settings import bot, dp
from src.core.logger import LOGGING
from src.core.middleware import DatabaseMiddleware

# from src.handlers import

loger = logging.getLogger(__name__)

commands = [
    types.BotCommand(command="start", description="запуск бота"),
    types.BotCommand(command="menu", description="Меню"),
]


# Функция, которая выполнится когда бот запустится
async def start_bot():
    await bot.send_message(288680459, f"Бот запущен")
    loger.info("Бот успешно запущен.")


# Функция, которая выполнится когда бот завершит свою работу
async def stop_bot():
    await bot.send_message(288680459, "Бот остановлен")
    loger.error("Бот остановлен!")


async def main():
    # регистрация роутов
    # dp.include_router(buy_virtual_network.router)

    # регистрация мидлварей
    dp.update.middleware.register(DatabaseMiddleware())

    # регистрация функций
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    try:
        await bot.set_my_commands(commands=commands)
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.config.dictConfig(LOGGING)
    asyncio.run(main())
