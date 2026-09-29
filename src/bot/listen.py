import random

from telebot.types import Message, ReactionTypeEmoji

import src.bot
import src.bot.send
import src.configs.config
import src.db
import src.text
from src.logger import logger


async def remember_message(m: Message):
    if not (src.configs.config.listener_rng_remember_enabled
            and random.randint(1, 1000) <= src.configs.config.listener_rng_remember):
        return

    logger.info(f"Remembering {m.id} message: {m.content_type}")

    if m.text and src.configs.config.listener_type_remember_message:
        await src.db.message.append(m, text=m.text)
    elif m.video and src.configs.config.listener_type_remember_video:
        await src.db.message.append(m, text=m.caption, video=m.video.file_id)
    elif m.video_note and src.configs.config.listener_type_remember_video_message:
        await src.db.message.append(m, video_message=m.video_note.file_id)
    elif m.photo and src.configs.config.listener_type_remember_picture:
        await src.db.message.append(m, text=m.caption, picture=m.photo[-1].file_id)
    elif m.voice and src.configs.config.listener_type_remember_voice_message:
        await src.db.message.append(m, voice_message=m.voice.file_id)
    elif m.sticker and src.configs.config.listener_type_remember_sticker:
        await src.db.message.append(m, sticker=m.sticker.file_id)
    elif m.animation and src.configs.config.listener_type_remember_animation:
        await src.db.message.append(m, animation=m.animation.file_id)


async def learn_markov(m: Message):
    text = m.text or m.caption
    if not (text and src.configs.config.listener_markov_enabled
            and random.randint(1, 1000) <= src.configs.config.listener_markov_learn_chance):
        return

    logger.info("markov trying to learn text")

    words = src.text.split_words(text)
    if words and len(words) > 1:
        pairs = [(words[i].lower(), words[i + 1].lower()) for i in range(len(words) - 1)]
        await src.db.markov.insert_pairs(pairs)
        logger.info(f"learned {len(pairs)} pairs")
    else:
        logger.info(f"insufficient words in message, or words not found: {words}")


async def react_with_emoji(m: Message):
    if not (src.configs.config.emoji_reactions_enabled
            and random.randint(1, 1000) <= src.configs.config.emoji_reactions_chance):
        return

    emojis = src.configs.config.emoji_reactions_available.split(" ")
    if not emojis:
        return

    random_emoji = random.choice(emojis)
    logger.info(f"Reacting {random_emoji} for {m.message_id} message")

    try:
        await src.bot.bot.set_message_reaction(
            m.chat.id,
            m.message_id,
            reaction=[ReactionTypeEmoji(random_emoji)]
        )
    except Exception as e:
        logger.error(f"An error occurred on emoji reaction for: {random_emoji} | {e}", exc_info=True)


async def listen_chat(m: Message):
    logger.info(f"New {m.id} message income ({m.content_type=} | {m.chat.id=})")

    logger.info(f"[listen] {m.id}: checking remember")
    await remember_message(m)

    logger.info(f"[listen] {m.id}: checking markov learn")
    await learn_markov(m)

    logger.info(f"[listen] {m.id}: trying markov continuation")
    if not await src.bot.send.maybe_send_markov(m):
        logger.info(f"[listen] {m.id}: trying content send")
        await src.bot.send.maybe_send(m)

    logger.info(f"[listen] {m.id}: checking emoji reaction")
    await react_with_emoji(m)