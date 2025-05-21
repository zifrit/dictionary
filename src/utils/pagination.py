from typing import Any, Coroutine

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Dictionary, Topic
from src.repository.dictionary import DictionaryManager, TopicManager
from src.kbs.pagination import Pagination, create_pagination_buttons
from src.kbs.other import move_to


def prep_text(
    data: list[Dictionary | Topic], fields: dict[str, str | dict]
) -> list[str]:
    text: list[str] = []
    for obj in data:  # type: Dictionary | Topic
        intermediate_text = []
        for key, value in fields.items():
            if isinstance(value, dict):
                if value["action"] == "len":
                    intermediate_text.append(f"{value[key]}: {len(getattr(obj, key))}")
                elif value["action"] == "int":
                    intermediate_text.append(f"{value[key]}: {int(getattr(obj, key))}")
                elif value["action"] == "str":
                    intermediate_text.append(f"{value[key]}: {str(getattr(obj, key))}")
            else:
                intermediate_text.append(f"{value}: {getattr(obj, key)}")
        text.append("\n".join(intermediate_text))
    return text


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


def item_buttons(
    data: list[DictionaryManager | TopicManager],
    title_key: str,
    item_callback_data: str,
) -> list[InlineKeyboardButton]:
    buttons: list[InlineKeyboardButton] = []
    for obj in data:  # type: Dictionary | Topic
        buttons.append(
            InlineKeyboardButton(
                text=f"{getattr(obj, title_key)}",
                callback_data=f"{item_callback_data}_{obj.id}",
            )
        )
    return buttons


async def pagination(
    session: AsyncSession,
    count_data_in_page: int,
    model_manage: DictionaryManager | TopicManager,
    fields: dict[str, str | dict],
    start: bool = True,
    filters: dict[str, str | int] | None = None,
    pagination_callback_data: Pagination | None = None,
    item_callback_data: str | None = None,
    title_key: str | None = None,
    prev_action_text: str | None = None,
    nex_action_text: str | None = None,
) -> tuple[str, InlineKeyboardMarkup] | tuple[str, None] | None:
    if filters is None:
        filters = dict()
    item_inline_buttons = []

    if start:
        objects, count_objects = await model_manage.get_pagination(
            session=session, limit=count_data_in_page, **filters
        )
        count_page = (
            count_objects // count_data_in_page + 1
            if count_objects % count_data_in_page != 0
            else count_objects // count_data_in_page
        )

        if item_callback_data is not None:
            item_inline_buttons = item_buttons(
                data=objects, title_key=title_key, item_callback_data=item_callback_data
            )

        text = prep_text(objects, fields)
        if 0 <= count_objects <= count_data_in_page:
            reply_markup: InlineKeyboardBuilder = create_pagination_buttons(
                count_page=count_page,
            )
            return (
                "\n\n".join(text),
                reply_markup.row(*item_inline_buttons, width=1).as_markup(),
            )

        reply_markup = create_pagination_buttons(
            name_nex_action=nex_action_text,
            count_page=count_page,
        )
        return (
            "\n\n".join(text),
            reply_markup.row(*item_inline_buttons, width=1).as_markup(),
        )
    else:
        page = 0
        if pagination_callback_data.action == prev_action_text:
            if pagination_callback_data.page > 1:
                page = pagination_callback_data.page - 1
                if page <= 1:
                    prev_action_text = None
            else:
                page = pagination_callback_data.page
                prev_action_text = None
        elif pagination_callback_data.action == nex_action_text:
            if pagination_callback_data.page < pagination_callback_data.count_page:
                page = pagination_callback_data.page + 1
                if page >= pagination_callback_data.count_page:
                    nex_action_text = None
            else:
                page = pagination_callback_data.page
                nex_action_text = None
        objects, count_objects = await model_manage.get_pagination(
            session=session, limit=count_data_in_page, offset=page, **filters
        )
        count_page = (
            count_objects // count_data_in_page + 1
            if count_objects % count_data_in_page != 0
            else count_objects // count_data_in_page
        )
        text = prep_text(objects, fields)
        reply_markup = create_pagination_buttons(
            count_page=count_page,
            page=page,
            name_prev_action=prev_action_text,
            name_nex_action=nex_action_text,
        )

        if item_callback_data is not None:
            item_inline_buttons = item_buttons(
                data=objects, title_key=title_key, item_callback_data=item_callback_data
            )

        return (
            "\n\n".join(text),
            reply_markup.row(*item_inline_buttons, width=1).as_markup(),
        )
