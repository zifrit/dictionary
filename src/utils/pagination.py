from typing import Any, Coroutine

from aiogram.types import InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Dictionary, Topic
from src.repository.dictionary import DictionaryManager, TopicManager
from src.kbs.pagination import Pagination, pagination as kbs_pagination
from src.kbs.other import move_to


def prep_text(data: list, fields: dict[str, str | dict]) -> list[str]:
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


async def pagination(
    session: AsyncSession,
    count_data_in_page: int,
    model_manage: DictionaryManager | TopicManager,
    fields: dict[str, str | dict],
    start: bool = True,
    filters: dict[str, str | int] | None = None,
    callback_data: Pagination | None = None,
    prev_action_text: str | None = None,
    nex_action_text: str | None = None,
) -> tuple[str, InlineKeyboardMarkup] | tuple[str, None] | None:
    if filters is None:
        filters = dict()
    if start:
        objects, count_objects = await model_manage.get_pagination(
            session=session, limit=count_data_in_page, **filters
        )
        count_page = (
            count_objects // count_data_in_page + 1
            if count_objects % count_data_in_page != 0
            else count_objects // count_data_in_page
        )
        if 0 < count_objects <= count_data_in_page:
            text = prep_text(objects, fields)
            return "\n\n".join(text), None

        elif count_objects > count_data_in_page:
            text = prep_text(objects, fields)
            reply_markup = kbs_pagination(
                name_nex_action=nex_action_text,
                count_page=count_page,
            )
            return "\n\n".join(text), reply_markup
    else:
        page = 0
        if callback_data.action == prev_action_text:
            if callback_data.page > 1:
                page = callback_data.page - 1
                if page <= 1:
                    prev_action_text = None
            else:
                page = callback_data.page
                prev_action_text = None
        elif callback_data.action == nex_action_text:
            if callback_data.page < callback_data.count_page:
                page = callback_data.page + 1
                if page >= callback_data.count_page:
                    nex_action_text = None
            else:
                page = callback_data.page
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
        reply_markup = kbs_pagination(
            count_page=count_page,
            page=page,
            name_prev_action=prev_action_text,
            name_nex_action=nex_action_text,
        )

        return "\n\n".join(text), reply_markup
