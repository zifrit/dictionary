from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


about_dictionary = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Список топиков",
                callback_data="list_topics",
            )
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)
