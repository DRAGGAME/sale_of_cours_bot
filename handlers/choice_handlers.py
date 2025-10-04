from aiogram import Router, F
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
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
        self.router_choice.callback_query.register(self.choice_page, ChoiceCourse.filter(F.action != None))

    async def choice_course(self, callback: CallbackQuery, callback_data: CallbackData, state: FSMContext):
        number_course_id: int = callback_data.number_course_id
        course = await self.database.select_course(int(number_course_id))


        keyboard_back = await self.choice_fabric_keyboard.inline_pay_keyboard(course[2])
        await state.update_data(data_course=tuple(course))

        await callback.message.edit_text(f"<pre>"
                                             f"Название курса: {course[1]}"
                                             f"\nОписание курса: {course[-2]}"
                                             f"\n\nЦена курса: {course[-4]}\n</pre>", reply_markup=keyboard_back)
        await callback.answer()

    async def choice_page(self, callback: CallbackQuery, callback_data: CallbackData, state: FSMContext):
        page = callback_data.page
        action = callback_data.action
        all_courses = await state.get_value("all_courses")
        if action == "next" and page < len(all_courses)-1 :
            page += 1
        elif action == "back" and page > 0:
            page -= 1
        else:
            await callback.answer("Дальше курсов нет", show_alert=True)
            return

        kb = await self.choice_fabric_keyboard.inline_choice_course_keyboard(all_courses, page)

        await callback.message.edit_text("Выберите курс", reply_markup=kb)
        await callback.answer()

