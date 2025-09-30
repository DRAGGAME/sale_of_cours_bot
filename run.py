import asyncio
import logging

from aiogram import Dispatcher

from database.admin_operations import AdminOperation
from database.create_table import CreateTable

from config import bot
from database.user_operation import UserOperation
from handlers.begin_handlers import BeginHandler

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] #%(levelname)-4s %(filename)s:'
           '%(lineno)d - %(name)s - %(message)s'
)

dp = Dispatcher()

class TelegramBot:
    def __init__(self, database: UserOperation, admin_database: AdminOperation):
        self.bot = bot
        self.dp = Dispatcher()

        self.begin_handlers = BeginHandler()

        self.dp.include_routers(self.begin_handlers.router)

    async def run_main(self):

        sqlbase_create_table = CreateTable()

        await sqlbase_create_table.connect()
        # await sqlbase_create_table.init_pgcrypto()
        await sqlbase_create_table.create_accepted_users_table()
        await sqlbase_create_table.create_settings_table()
        await sqlbase_create_table.create_course_table()
        await sqlbase_create_table.create_transaction_table()

        await sqlbase_create_table.close()
        await asyncio.run(TelegramBot.run_main())

if __name__ == "__main__":
    asyncio.run(main())
