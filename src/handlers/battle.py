import asyncio
import logging
import random
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from src.kbs.words import battle_words_inline
from src.models import TopicBattles
from src.repository.dictionary import topic_manager, words_manager
from src.repository.tg_user import tg_user_manager

loger = logging.getLogger("admin_log")


router = Router()


@router.message(F.text.startswith("/about_topic_battle"))
async def about_topic_battle(message: Message, db_session: AsyncSession):
    await message.answer(
        text="""
Базовый запуск игры /start_topic_battle

С выбором топика /start_topic_battle "идентификатор топика". Между командой и идентификатором должен быть пробел. Например: /start_topic_battle 1

С выбором пользователей /start_topic_battle "@пользователь1" "@пользователь2" ... Пользователей нужно передавать через пробел. Например: /start_topic_battle @zifrit_1 @zifrit_2

С выбором пользователей и топика /start_topic_battle "идентификатор топика" "@пользователь1" "@пользователь2" ... Например: /start_topic_battle 12 @zifrit_1 @zifrit_2

Если после команды нету ничего то но запустить игру со всеми пользователями которые знает бот и случайным топиком.
        """
    )


@router.message(F.text.startswith("/start_topic_battle"))
async def start_topic_battle(message: Message, db_session: AsyncSession):
    split_text = message.text.split()
    if len(split_text) > 1 and not split_text[1].isdigit() and split_text[1][0] != "@":
        await message.reply("Не правильный формат")
        return
    elif len(split_text) == 1:
        battle: TopicBattles = await topic_manager.start_battle(
            db_session, chat_id=message.chat.id
        )
        # await message.answer(
        #     text=f"Топик:{battle.topic_id}\nИграют:Все кого знает бот в этом чате"
        # )
    elif len(split_text) == 2:
        if not split_text[1].isdigit():
            await message.reply("Не правильный формат")
            return
        battle: TopicBattles = await topic_manager.start_battle(
            db_session, chat_id=message.chat.id, topic_id=int(split_text[1])
        )
        # await message.answer(
        #     text=f"Топик:{battle.topic_id}\nИграют:Все кого знает бот в этом чате"
        # )
    elif len(split_text) > 2:
        if not split_text[1].isdigit():
            await message.reply("Не правильный формат")
            return
        players = [player[1:] for player in split_text[2:]]
        battle: TopicBattles = await topic_manager.start_battle(
            db_session,
            chat_id=message.chat.id,
            topic_id=int(split_text[1]),
            players=players,
        )
        # await message.answer(
        #     text=f"Топик:{battle.topic_id}\nИграют: {', '.join(players)}"
        # )

    random_three_words = await words_manager.get_random_three_words(session=db_session)
    battle_words = list(battle.words)
    random_element = random.choice(battle_words)
    battle_words.remove(random_element)
    battle.words = battle_words
    battle.used_words = [random_element]
    words = [
        {
            "text": word.word_translation,
            "call_back_data": f"check_battle_wrong_{battle.id}",
        }
        for word in random_three_words
    ]
    words.append(
        {
            "text": random_element["translate"],
            "call_back_data": f"check_battle_right_{battle.id}",
        }
    )
    text = f"""
           {random_element["word"]}
            """
    await message.answer(text, reply_markup=battle_words_inline(words))


@router.callback_query(F.data.startswith("check_battle"))
async def check_battle_answer(call: CallbackQuery, db_session: AsyncSession):
    print(call.message.text)
    _, _, answer, battle_id = call.data.split("_")
    battle = await topic_manager.get_battle(db_session, battle_id=int(battle_id))
    random_three_words = await words_manager.get_random_three_words(session=db_session)
    if answer == "wrong":
        score = dict(battle.players)
        score[str(call.from_user.id)] -= 1
        battle.players = score
    elif answer == "right":
        score = dict(battle.players)
        score[str(call.from_user.id)] += 1
        battle.players = score
    if not battle.words:
        text = []
        for tg_user_id, point in battle.players.items():
            tg_user = await tg_user_manager.get_by_id(db_session, id_=int(tg_user_id))
            text.append(f"{tg_user.username} - {point}")
        await call.message.edit_text(text="\n".join(text))
    else:
        battle_words = list(battle.words)
        random_element = random.choice(battle_words)
        battle_words.remove(random_element)
        battle.words = battle_words
        battle.used_words = [random_element, *battle.used_words]
        words = [
            {
                "text": word.word_translation,
                "call_back_data": f"check_battle_wrong_{battle.id}",
            }
            for word in random_three_words
        ]
        words.append(
            {
                "text": random_element["translate"],
                "call_back_data": f"check_battle_right_{battle.id}",
            }
        )
        text = f"""
               {random_element["word"]}
                """
        await asyncio.sleep(0.2)
        await call.message.edit_text(text, reply_markup=battle_words_inline(words))
