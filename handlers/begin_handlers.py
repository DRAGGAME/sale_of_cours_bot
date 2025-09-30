import asyncio

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery

from config import bot
from database.admin_operations import AdminOperation
from database.user_operation import UserOperation
from filters.check_admin import CheckAdminDefault
from keyboards.menu_fabric import FabricInline, ChoiceCallback


class BeginHandler:

    def __init__(self):
        self.bot = bot

        self.router = Router()
        self.database = UserOperation()
        self.admin_database = AdminOperation()
        self.begin_fabric_keyboard = FabricInline()

        self.register_handlers()

    def register_handlers(self):
        self.router.message.register(self.start_handler, CheckAdminDefault(self.database), CommandStart())
        self.router.callback_query.register(
            self.callback_politics_handler, ChoiceCallback.filter(F.accept))

    async def start_handler(self, message: Message):
        await self.database.connect()
        await self.admin_database.connect()

        politics = await self.database.select_politics()


        keyboard_start = await self.begin_fabric_keyboard.inline_choice_keyboard()

        await message.answer(text=f"Перед тем как воспользоваться ботом, "
                                  f"прочтите и примите это: \n"
                                  f"1) <a href=google.com>Политику кондфинициальности</a>\n"
                                  f"2) <a href={politics[-2]}>Пользовательское соглашение</a>",
                             reply_markup=keyboard_start)

    async def callback_politics_handler(self, callback: CallbackQuery, callback_data: CallbackData):

        accept_or_reject = callback_data.accept

        if accept_or_reject:
            await self.admin_database.insert_new_user(str(callback.message.chat_id))
            await callback.message.edit_text("Выберите курс")
            await callback.answer()
        else:
            await callback.message.edit_text("Вы отказались\nДальнейшие пользование ботом невозможно")
            await callback.answer()
            await asyncio.sleep(20)
            await callback.message.delete()
        await self.admin_database.close()
        await self.database.close()
