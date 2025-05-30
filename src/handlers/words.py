import logging
from contextlib import suppress

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from src.kbs.other import move_to
from src.kbs.pagination import Pagination
from src.kbs.topic import about_topic
from src.kbs.words import study_words
from src.states.dictionary import SearchTopic
from src.repository.dictionary import words_manager, topic_manager
from src.utils.pagination import pagination

loger = logging.getLogger("admin_log")


router = Router()


@router.callback_query(F.data.startswith("start_words"))
@router.callback_query(F.data.startswith("continue_words"))
async def start_study_words(
    call: CallbackQuery, db_session: AsyncSession, state: FSMContext
):
    await state.clear()
    topic_id = int(call.data.split("_")[-1])
    await topic_manager.check_started(
        session=db_session, topic_id=int(topic_id), tg_id=call.from_user.id
    )
    random_three_words = await words_manager.get_random_three_words(session=db_session)
    current_word = await words_manager.get_random_word_trys(
        session=db_session, topic_id=int(topic_id), tg_id=call.from_user.id
    )
    words = [
        {
            "text": word.word_translation,
            "call_back_data": f"check_answer_wrong_{topic_id}_{current_word.id}",
        }
        for word in random_three_words
    ]
    words.append(
        {
            "text": current_word.word.word_translation,
            "call_back_data": f"check_answer_right_{topic_id}_{current_word.id}",
        }
    )
    text = f"""
       {current_word.word.word}
       
       
Количество попыток
 ├ {current_word.trys}
"""
    await call.message.edit_text(text, reply_markup=study_words(words, topic_id))


@router.callback_query(F.data.startswith("check_answer"))
async def check_answer(call: CallbackQuery, db_session: AsyncSession):
    _, _, answer, topic_id, word_id = call.data.split("_")
    word = await words_manager.get_trys(db_session, id_=int(word_id))
    word_trys = word.trys[:4]
    if answer == "wrong":
        word.trys = "❌" + word_trys
    elif answer == "right":
        word.trys = "✅" + word_trys
    await db_session.flush()
    progress = await words_manager.check_result(
        session=db_session, topic_id=int(topic_id), tg_id=call.from_user.id
    )
    topic = await topic_manager.get_tg_user_progress(
        db_session, topic_id=int(topic_id), tg_id=call.from_user.id
    )
    if progress == 100:
        topic.progress = progress
        await call.message.edit_text(
            "Вы выучили все слова из топика",
            reply_markup=move_to(
                text="Назад🔙",
                callback_data=f"back_to_topic_{topic_id}",
            ),
        )
    else:
        topic.progress = progress
        await db_session.flush()

        random_three_words = await words_manager.get_random_three_words(
            session=db_session
        )
        current_word = await words_manager.get_random_word_trys(
            session=db_session, topic_id=int(topic_id), tg_id=call.from_user.id
        )
        words = [
            {
                "text": word.word_translation,
                "call_back_data": f"check_answer_wrong_{topic_id}_{current_word.id}",
            }
            for word in random_three_words
        ]
        words.append(
            {
                "text": current_word.word.word_translation,
                "call_back_data": f"check_answer_right_{topic_id}_{current_word.id}",
            }
        )
        text = f"""
       {current_word.word.word}


Количество попыток
 ├ {current_word.trys}
        """
        await call.message.edit_text(
            text, reply_markup=study_words(words, int(topic_id))
        )
