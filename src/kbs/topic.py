from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def about_topic(topic_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Начать изучать",
            callback_data=f"start_words_{topic_id}",
        ),
        InlineKeyboardButton(
            text="Сброс прогресса",
            callback_data=f"reset_topic_progress_{topic_id}",
        ),
        width=1,
    )
    return builder.as_markup()
