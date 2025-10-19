import os

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
load_dotenv()

TG_KEY = os.getenv('TG_API')

HOST_POSTGRES = os.getenv('HOST_POSTGRES')
USER_POSTGRES = os.getenv('USER_POSTGRES')
PASSWORD_POSTGRES = os.getenv('PASSWORD_POSTGRES')
DATABASE_POSTGRES = os.getenv('DATABASE_POSTGRES')

HOST_REDIS = os.getenv('HOST_REDIS')
PASSWORD_REDIS = os.getenv('PASSWORD_REDIS')
REDIS_DATABASES = os.getenv('REDIS_DATABASES')
URL_REDIS = f"redis://:{PASSWORD_REDIS}@{HOST_REDIS}:6379/{REDIS_DATABASES}"

PASSWORD_ADMIN = os.getenv('PASSWORD_ADMIN')
PROVIDER_TOKEN = os.getenv('PROVIDER_TOKEN')

bot = Bot(token=TG_KEY, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

