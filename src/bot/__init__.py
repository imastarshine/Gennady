from telebot import asyncio_filters
from telebot.async_telebot import AsyncTeleBot
from src.shared import TELEGRAM_BOT_TOKEN
import src.bot.register

# noinspection PyTypeChecker
bot = AsyncTeleBot(TELEGRAM_BOT_TOKEN)
bot.add_custom_filter(asyncio_filters.StateFilter(bot))
