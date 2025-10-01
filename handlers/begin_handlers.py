import asyncio

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery

from config import bot
from database.admin_operations import AdminOperation
from database.user_operation import UserOperation
from filters.check_admin import CheckAdminDefault
from keyboards.menu_fabric import ChoiceCallback, FabricInline
from aiogram.types import Message

class BeginHandler:

    def __init__(self):
        self.bot = bot

        self.router = Router()
        self.database = UserOperation()       # пул уже есть
        self.admin_database = AdminOperation()
        self.begin_fabric_keyboard = FabricInline()

        self.register_handlers()

    def register_handlers(self):
        self.router.message.register(self.start_handler, CheckAdminDefault(self.database), CommandStart())
        self.router.callback_query.register(
            self.callback_politics_handler, ChoiceCallback.filter(F.accept))

    async def start_handler(self, message: Message):
        politics = await self.database.select_politics()
        keyboard_start = await self.begin_fabric_keyboard.inline_choice_keyboard()

        await message.answer(
            text=f"Перед тем как воспользоваться ботом, "
                 f"прочтите и примите это: \n"
                 f"1) <a href=google.com>Политику кондфинициальности</a>\n"
                 f"2) <a href={politics[-2]}>Пользовательское соглашение</a>",
            reply_markup=keyboard_start
        )

    async def callback_politics_handler(self, callback: CallbackQuery, callback_data: CallbackData):
        if callback_data.accept:
            await self.admin_database.insert_new_user(str(callback.message.chat.id))
            all_courses = await self.database.select_all_courses()
            if all_courses:
                kb = await self.begin_fabric_keyboard.inline_choice_course_keyboard(all_courses, 0)
                await callback.message.edit_text("Выберите курс", reply_markup=kb)
            else:
                await callback.message.edit_text("Нет доступных курсов...")
        else:
            await callback.message.edit_text("Вы отказались\nДальнейшее пользование ботом невозможно")
            await asyncio.sleep(20)
            await callback.message.delete()

        await callback.answer()
