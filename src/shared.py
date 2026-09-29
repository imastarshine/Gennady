import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_TO_LISTEN = int(os.getenv("TELEGRAM_CHAT_TO_LISTEN"))
TELEGRAM_BOT_SOCKS5_PROXY = os.getenv("TELEGRAM_BOT_SOCKS5_PROXY")
