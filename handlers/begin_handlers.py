import asyncio

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message
from asyncpg import UniqueViolationError

from config import bot
from database.admin_operations import AdminOperation
from database.user_operation import UserOperation
from filters.check_admin import CheckRegistryUser, CheckSelectUser
from keyboards.menu_fabric import ChoiceCallback, FabricInline
from logger import logger


class BeginHandler:
    """
    Класс, созданный для начала работы с ботом
    """
    def __init__(self):
        self.bot = bot

        self.router = Router()

        self.database = UserOperation()
        self.admin_database = AdminOperation()

        self.begin_fabric_keyboard = FabricInline()

        self.register_handlers()

    def register_handlers(self):
        self.router.message.register(self.start_handler, CheckRegistryUser(self.database), CommandStart())

        self.router.message.register(
            self.start_handler_nach_pay, CheckSelectUser(self.database), CommandStart())

        self.router.callback_query.register(
            self.callback_start_handler, ChoiceCallback.filter(F))

    async def start_handler(self, message: Message, state: FSMContext):
        try:
            logger.info("Появился новый пользователь\n"
                        f"{message.from_user.username}\n"
                        f"callback_data: {message.chat.id}\n")
            await self.admin_database.insert_new_user(str(message.chat.id))
        except UniqueViolationError:
            pass

        all_courses, main_message = await self.database.select_all_courses(True)

        if all_courses:
            if main_message == "0":
                main_message = "Выберите курс"

            await state.update_data(all_courses=all_courses)
            kb = await self.begin_fabric_keyboard.inline_choice_course_keyboard(all_courses, 0)

            await message.answer(f"{main_message}", reply_markup=kb)
        else:
            logger.warning("Нет доступных курсов")
            await message.answer(f"Нет доступных курсов...\n\nНапишите администратору бота, чтобы добавили курсы")

        await state.clear()

    async def callback_start_handler(self, callback: CallbackQuery, state: FSMContext):
        """
        Тот же start, но для callback
        :param callback:
        :param callback_data:
        :param state:
        :return:
        """

        all_courses, main_message = await self.database.select_all_courses(True)

        if all_courses:
            if main_message == "0":
                main_message = "Выберите курс"

            await state.update_data(all_courses=all_courses)
            kb = await self.begin_fabric_keyboard.inline_choice_course_keyboard(all_courses, 0)

            await callback.message.edit_text(f"{main_message}", reply_markup=kb)
        else:
            logger.warning("Нет доступных курсов")
            await callback.message.edit_text("Нет доступных курсов...\n\nНапишите администратору бота, чтобы добавили курсы")

        await state.clear()
        await callback.answer()

    async def start_handler_nach_pay(self, message: Message, state: FSMContext):
        await state.clear()

        all_courses, main_message = await self.database.select_all_courses(True)

        if all_courses:
            if main_message == "0":
                main_message = "Выберите курс"

            await state.update_data(all_courses=all_courses)
            kb = await self.begin_fabric_keyboard.inline_choice_course_keyboard(all_courses, 0)

            await message.answer(f"{main_message}", reply_markup=kb)

        else:
            logger.warning("Нет доступных курсов")
            await message.answer("Нет доступных курсов...\n\nНапишите администратору бота, чтобы добавили курсы")
