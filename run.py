# run.py
import asyncio
import logging

from aiogram import Dispatcher
from config import bot
from database.admin_operations import AdminOperation
from database.create_table import CreateTable
from database.user_operation import UserOperation
from database.db import Sqlbase
from handlers.begin_handlers import BeginHandler

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] #%(levelname)-4s %(filename)s:'
           '%(lineno)d - %(name)s - %(message)s'
)

dp = Dispatcher()


class TelegramBot:
    def __init__(self):
        self.bot = bot
        self.dp = Dispatcher()

        self.begin_handlers = BeginHandler()

        self.dp.include_router(self.begin_handlers.router)

    async def run_main(self):
        # один раз инициализируем пул

        sqlbase_create_table = CreateTable()

        await sqlbase_create_table.create_accepted_users_table()
        await sqlbase_create_table.create_settings_table()
        await sqlbase_create_table.create_course_table()
        await sqlbase_create_table.create_transaction_table()

        await self.dp.start_polling(self.bot)

        await Sqlbase.close_pool()


async def main():
    await Sqlbase.init_pool()
    tg_bot = TelegramBot()
    await tg_bot.run_main()


if __name__ == "__main__":
    asyncio.run(main())
