import asyncio
import logging

from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from config import bot, REDIS_URL
from database.create_table import CreateTable
from database.db import Sqlbase
from handlers.admin_handlers import AdminHandlers
from handlers.begin_handlers import BeginHandler
from handlers.choice_handlers import ChoiceHandlers
from handlers.pay_handlers import PayHandlers

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] #%(levelname)-4s %(filename)s:'
           '%(lineno)d - %(name)s - %(message)s'
)


class TelegramBot:
    """
    Класс главный телеграм-бота
    """
    def __init__(self):
        self.bot = bot
        self.dp = Dispatcher(storage=RedisStorage.from_url(REDIS_URL))

        self.admin_handlers = AdminHandlers()
        self.begin_handlers = BeginHandler()
        self.choice_handlers = ChoiceHandlers()
        self.pay_handlers = PayHandlers()

        self.dp.include_routers(self.begin_handlers.router, self.choice_handlers.router_choice,
                                self.pay_handlers.router_pay, self.admin_handlers.router)

    async def run_main(self):
        """
        Основной run
        :return:
        """
        sqlbase_create_table = CreateTable()

        await sqlbase_create_table.init_pgcrypto()
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
