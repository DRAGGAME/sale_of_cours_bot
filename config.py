import os

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
load_dotenv()

TG_KEY = os.getenv('TG_API')

HOST_POSTGRES = os.getenv('HOST_POSTGRES')
USER = os.getenv('user')
PASSWORD = os.getenv('password')
DATABASE = os.getenv('DATABASE')

HOST_REDIS = os.getenv('HOST_REDIS')
PASSWORD_REDIS = os.getenv('PASSWORD_REDIS')

PASSWORD_ADMIN = os.getenv('PASSWORD_ADMIN')
PROVIDER_TOKEN = os.getenv('PROVIDER_TOKEN')

REDIS_URL = f"redis://:{PASSWORD_REDIS}@{HOST_REDIS}:6379/0"
bot = Bot(token=TG_KEY, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

