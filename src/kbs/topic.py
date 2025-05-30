from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def about_topic(topic_id: int, start: bool = True) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if start:
        builder.row(
            InlineKeyboardButton(
                text="Начать изучать",
                callback_data=f"start_words_{topic_id}",
            ),
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text="Продолжить изучать",
                callback_data=f"continue_words_{topic_id}",
            ),
        )
    builder.row(
        InlineKeyboardButton(
            text="Сброс прогресса",
            callback_data=f"reset_topic_progress_{topic_id}",
        ),
        width=1,
    )
    return builder.as_markup()
