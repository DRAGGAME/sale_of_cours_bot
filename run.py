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
from handlers.choice_handlers import ChoiceHandlers
from keyboards.menu_fabric import ChoiceCourse
from handlers.pay_handlers import PayHandlers

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
        self.choice_handlers = ChoiceHandlers()
        self.pay_handlers = PayHandlers()

        self.dp.include_routers(self.begin_handlers.router, self.choice_handlers.router_choice, self.pay_handlers.router_pay)

    async def run_main(self):

        sqlbase_create_table = CreateTable()

        await sqlbase_create_table.create_accepted_users_table()
        await sqlbase_create_table.create_settings_table()
        await sqlbase_create_table.create_course_table()
        await sqlbase_create_table.create_transaction_table()

        await self.dp.start_polling(self.bot, skip_updates=False)

        await Sqlbase.close_pool()


async def main():
    await Sqlbase.init_pool()
    tg_bot = TelegramBot()
    await tg_bot.run_main()


if __name__ == "__main__":
    asyncio.run(main())
