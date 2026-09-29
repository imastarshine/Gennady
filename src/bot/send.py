import random

from telebot.types import Message

import src.bot
import src.bot.data
import src.configs
import src.db
import src.text
from src.logger import logger


def force_send(m: Message) -> bool:
    return (
        src.configs.config.listener_parameters_disable_rng_on_answer
        and m.reply_to_message
        and m.reply_to_message.from_user.id == src.bot.data.USER_ID
    )


async def maybe_send_markov(m: Message) -> bool:
    if not src.configs.config.sender_rng_sending_enabled:
        return False

    text = m.text or m.caption
    if not (text and src.configs.config.listener_markov_enabled
            and src.configs.config.listener_markov_prediction_enabled):
        return False

    if not force_send(m) and random.randint(1, 1000) > src.configs.config.listener_markov_prediction_chance:
        return False

    message_parts = [part.lower() for part in src.text.split_words(text)]
    if not message_parts:
        return False

    new_message_parts = []
    last_message = message_parts[-1]
    for i in range(random.randint(3, 6)):
        if not await src.db.markov.can_continue(last_message):
            break

        random_word = await src.db.markov.get_random_word(last_message)
        last_message = random_word
        new_message_parts.append(random_word)

    if not new_message_parts:
        return False

    message = " ".join(new_message_parts)
    await src.bot.bot.reply_to(m, message)
    return True


async def maybe_send(m: Message) -> bool:
    if not src.configs.config.sender_rng_sending_enabled:
        return False

    if not force_send(m) and random.randint(1, 1000) > src.configs.config.sender_rng_sending:
        return False

    chances = {
        "text": src.configs.config.sender_type_message_chance,
        "video": src.configs.config.sender_type_video_chance,
        "video_message": src.configs.config.sender_type_video_message_chance,
        "picture": src.configs.config.sender_type_picture_chance,
        "voice_message": src.configs.config.sender_type_voice_message_chance,
        "sticker": src.configs.config.sender_type_sticker_chance,
        "animation": src.configs.config.sender_type_animation_chance
    }

    available_content_types = await src.db.message.get_available_content_types()
    filtered_chances = {
        content_type: chances[content_type]
        for content_type in available_content_types
    }

    if not filtered_chances:
        return False

    content_type = random.choices(list(filtered_chances.keys()), weights=list(filtered_chances.values()), k=1)[0]
    content = await src.db.message.get_random_content(content_type)

    try:
        if content_type == "text":
            if random.randint(0, 100) <= 25:
                await src.bot.bot.reply_to(m, text=content)
            else:
                await src.bot.bot.send_message(m.chat.id, content)
        elif content_type == "video":
            await src.bot.bot.send_video(
                m.chat.id,
                content,
                reply_to_message_id=m.message_id if random.randint(0, 100) <= 25 else None
            )
        elif content_type == "video_message":
            await src.bot.bot.send_video_note(
                m.chat.id,
                content,
                reply_to_message_id=m.message_id if random.randint(0, 100) <= 25 else None
            )
        elif content_type == "picture":
            await src.bot.bot.send_photo(
                m.chat.id,
                content,
                reply_to_message_id=m.message_id if random.randint(0, 100) <= 25 else None
            )
        elif content_type == "voice_message":
            await src.bot.bot.send_voice(
                m.chat.id,
                content,
                reply_to_message_id=m.message_id if random.randint(0, 100) <= 25 else None
            )
        elif content_type == "sticker":
            await src.bot.bot.send_sticker(
                m.chat.id,
                content,
                reply_to_message_id=m.message_id if random.randint(0, 100) <= 25 else None
            )
        elif content_type == "animation":
            await src.bot.bot.send_animation(
                m.chat.id,
                content,
                reply_to_message_id=m.message_id if random.randint(0, 100) <= 25 else None
            )
    except Exception as e:
        logger.error(f"An error occurred on sending message: {content_type} | {content} | {e}", exc_info=True)
        return False

    return True