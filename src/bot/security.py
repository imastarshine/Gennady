import typing

from telebot.types import Message, CallbackQuery

import src.shared
import src.bot
from src.logger import logger

TEST_MODE = False


def restricted(func: typing.Callable) -> typing.Callable:
    async def wrapper(message: Message | CallbackQuery, *args, **kwargs):
        if TEST_MODE:
            return await func(message, *args, **kwargs)

        is_message = isinstance(message, Message)
        is_callback_query = isinstance(message, CallbackQuery)

        if ((is_message and message.chat.id == src.shared.TELEGRAM_CHAT_TO_LISTEN)
                or (is_callback_query and message.message and message.message.chat.id == src.shared.TELEGRAM_CHAT_TO_LISTEN)):

            if is_message and message.chat.type in ["private"]:
                return await func(message, *args, **kwargs)

            if is_callback_query and message.message.chat.type in ["private"]:
                return await func(message, *args, **kwargs)

            member = await src.bot.bot.get_chat_member(src.shared.TELEGRAM_CHAT_TO_LISTEN, message.from_user.id)
            if member.status in ['administrator', 'creator']:
                return await func(message, *args, **kwargs)
        else:
            logger.warning(f"user {message.from_user.username} {message.from_user.id} not allowed")
        return False

    return wrapper
