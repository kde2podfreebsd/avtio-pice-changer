import os
from db import QuoteController
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage
from utils import db_sqlite_path

load_dotenv()

bot = AsyncTeleBot(
    os.getenv("TELEGRAM_BOT_TOKEN"),
    state_storage=StateMemoryStorage(),
    disable_notification=False,
    colorful_logs=False
)

qc = QuoteController(db_sqlite_path)