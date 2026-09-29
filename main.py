import asyncio
import src.bot
import src.shared
import src.db
import src.configs
import src.bot.data
from src.logger import logger, cleanup_old_logs, enable_file_logging
from telebot import asyncio_helper


async def main():
    cleanup_old_logs(31)
    await src.db.message.init()
    await src.db.markov.init()

    if (src.shared.TELEGRAM_BOT_SOCKS5_PROXY
            and isinstance(src.shared.TELEGRAM_BOT_SOCKS5_PROXY, str)
            and src.shared.TELEGRAM_BOT_SOCKS5_PROXY.startswith("socks5")):
        asyncio_helper.proxy = src.shared.TELEGRAM_BOT_SOCKS5_PROXY

    logger.info("gathering bot information")
    info = await src.bot.bot.get_me()
    src.bot.data.USER_ID = info.id
    logger.info(f"found bot id: {src.bot.data.USER_ID}")

    enable_file_logging()

    logger.info("trying to register handlers")
    await src.bot.register.register()
    logger.info("starting infinity polling")
    await src.bot.bot.infinity_polling()


if __name__ == "__main__":
    src.configs.config.load()
    asyncio.run(main())
    src.configs.config.save()