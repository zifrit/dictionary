import random
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def study_words(words: list[dict[str, str]], topic_id: int) -> InlineKeyboardMarkup:
    random.shuffle(words)
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=words[0]["text"],
            callback_data=words[0]["call_back_data"],
        ),
        InlineKeyboardButton(
            text=words[1]["text"],
            callback_data=words[1]["call_back_data"],
        ),
        InlineKeyboardButton(
            text=words[2]["text"],
            callback_data=words[2]["call_back_data"],
        ),
        InlineKeyboardButton(
            text=words[3]["text"],
            callback_data=words[3]["call_back_data"],
        ),
        InlineKeyboardButton(
            text="Назад🔙",
            callback_data=f"back_to_topic_{topic_id}",
        ),
        width=2,
    )
    return builder.as_markup()


def battle_words_inline(words: list[dict[str, str]]) -> InlineKeyboardMarkup:
    random.shuffle(words)
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=words[0]["text"],
            callback_data=words[0]["call_back_data"],
        ),
        InlineKeyboardButton(
            text=words[1]["text"],
            callback_data=words[1]["call_back_data"],
        ),
        InlineKeyboardButton(
            text=words[2]["text"],
            callback_data=words[2]["call_back_data"],
        ),
        InlineKeyboardButton(
            text=words[3]["text"],
            callback_data=words[3]["call_back_data"],
        ),
        width=1,
    )
    return builder.as_markup()
