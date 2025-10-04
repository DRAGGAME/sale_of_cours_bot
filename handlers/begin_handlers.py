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


class BeginHandler:

    def __init__(self):
        self.bot = bot

        self.router = Router()
        self.database = UserOperation()  # пул уже есть
        self.admin_database = AdminOperation()
        self.begin_fabric_keyboard = FabricInline()

        self.register_handlers()

    def register_handlers(self):
        self.router.message.register(self.start_handler, CheckRegistryUser(self.database), CommandStart())

        self.router.callback_query.register(
            self.callback_politics_handler, ChoiceCallback.filter(F))

        self.router.message.register(
            self.start_handler_nach_pay, CheckSelectUser(self.database), CommandStart())

    async def start_handler(self, message: Message):
        await bot.unpin_all_chat_messages(message.chat.id)
        politics = await self.database.select_politics()
        keyboard_start = await self.begin_fabric_keyboard.inline_choice_keyboard()

        msg_pin = await message.answer(
            text=f"Перед тем как воспользоваться ботом, "
                 f"прочтите и примите это: \n"
                 f"1) <a href={politics[-1]}>Политику кондфинициальности</a>\n"
                 f"2) <a href={politics[-2]}>Пользовательское соглашение</a>",
            reply_markup=keyboard_start
        )
        await bot.pin_chat_message(chat_id=message.chat.id, message_id=msg_pin.message_id)

    async def callback_politics_handler(self, callback: CallbackQuery, callback_data: CallbackData, state: FSMContext):
        await state.clear()
        print(callback_data.accept)
        if callback_data.accept:
            try:
                await self.admin_database.insert_new_user(str(callback.message.chat.id))
            except UniqueViolationError:
                pass
            all_courses = await self.database.select_all_courses()
            if all_courses:
                await state.update_data(all_courses=all_courses)
                kb = await self.begin_fabric_keyboard.inline_choice_course_keyboard(all_courses, 0)

                msg_pin = await callback.message.edit_text("Выберите курс", reply_markup=kb)
                await bot.pin_chat_message(chat_id=msg_pin.chat.id, message_id=msg_pin.message_id)
            else:
                await callback.message.edit_text("Нет доступных курсов...")
        else:
            await callback.message.edit_text("Вы отказались\nДальнейшее пользование ботом невозможно")
            await asyncio.sleep(20)
            await callback.message.delete()

        await callback.answer()

    async def start_handler_nach_pay(self, message: Message, state: FSMContext):
        await state.clear()

        all_courses = await self.database.select_all_courses()
        if all_courses:
            await state.update_data(all_courses=all_courses)
            kb = await self.begin_fabric_keyboard.inline_choice_course_keyboard(all_courses, 0)
            await message.answer("Выберите курс", reply_markup=kb)
        else:
            await message.answer("Нет доступных курсов...")
