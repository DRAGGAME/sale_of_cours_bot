from aiogram import Router, F
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery

from config import bot
from database.admin_operations import AdminOperation
from database.user_operation import UserOperation
from keyboards.menu_fabric import FabricInline, ChoiceCourse


class ChoiceHandlers:
    def __init__(self):
        self.bot = bot
        self.router_choice = Router()

        self.database = UserOperation()       # пул уже есть
        self.admin_database = AdminOperation()
        self.choice_fabric_keyboard = FabricInline()

        self.register_handlers()

    def register_handlers(self):
        self.router_choice.callback_query.register(self.choice_course, ChoiceCourse.filter(F.number_course_id != None))

    async def choice_course(self, callback: CallbackQuery, callback_data: CallbackData):
        number_course_id: int = callback_data.number_course_id
        print(number_course_id)
        course = await self.database.select_course(int(number_course_id))

        keyboard_back = await self.choice_fabric_keyboard.inline_back_button()
        await callback.message.edit_text(f"<pre>"
                                         f"Название курса: {course[1]}"
                                         f"\nОписание курса: {course[-1]}"
                                         f"\n\nЦена курса: {course[-3]}\n</pre>", reply_markup=keyboard_back)
        await callback.answer()