import src.bot
import src.bot.listen
import src.bot.settings
import src.bot.security
import src.bot.states
from src.shared import TELEGRAM_CHAT_TO_LISTEN


async def register():

    # settings.py
    src.bot.bot.register_message_handler(
        callback=src.bot.security.restricted(src.bot.settings.settings_command),
        commands=["settings"]
    )
    src.bot.bot.register_message_handler(
        callback=src.bot.settings.set_int_config_item,
        state=src.bot.states.UserSteps.waiting_for_setting_int_value
    )

    src.bot.bot.register_message_handler(
        callback=src.bot.settings.set_str_config_item,
        state=src.bot.states.UserSteps.waiting_for_setting_str_value
    )

    src.bot.bot.register_callback_query_handler(
        callback=src.bot.security.restricted(src.bot.settings.process_settings_callback),
        func=lambda call: call.data.startswith("e:")
    )

    # listen.py
    src.bot.bot.register_message_handler(
        callback=src.bot.listen.listen_chat,
        func=lambda m: m.chat.id == TELEGRAM_CHAT_TO_LISTEN,
        content_types=['text', 'photo', 'video', 'video_note', 'voice', 'sticker', 'animation'],
        state=None
    )

