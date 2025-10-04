import asyncio
from typing import Awaitable

from aiogram import Router, F
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from asyncpg import UniqueViolationError, DataError

from config import bot
from database.admin_operations import AdminOperation
from filters.check_admin import CheckAdmin
from keyboards.admin_fabric import AdminFabric, StopInline


class SetupStates(StatesGroup):
    name = State()
    description = State()
    price = State()
    channel = State()
    none_state = State()

class SetupFSM(StatesGroup):
    setup_password = State()


class AdminHandlers:

    def __init__(self):
        self.bot = bot

        self.router = Router()
        self.admin_database = AdminOperation()
        self.begin_fabric_keyboard = AdminFabric()

        self.register_handlers_is_admin()

    def register_handlers_is_admin(self):
        self.router.channel_post.register(self.chat_id_handler, Command("chat_id"))

        self.router.message.register(self.setup_handler, Command("setup"))
        self.router.message.register(self.setup_from_password_handler, SetupFSM.setup_password)

        self.router.message.register(self.add_new_course, Command("add_channel"), CheckAdmin(self.admin_database))

        self.router.callback_query.register(self.edit_course, StopInline.filter(F.action), SetupStates.none_state)

        self.router.message.register(self.edit_komponent_course, F, SetupStates.name)
        self.router.message.register(self.edit_komponent_course, F, SetupStates.description)
        self.router.message.register(self.edit_komponent_course, F, SetupStates.price)
        self.router.message.register(self.edit_komponent_course, F, SetupStates.channel)




    async def setup_handler(self, message: Message, state: FSMContext):
        password = await self.admin_database.select_password_and_user()
        await state.clear()

        if password:
            await state.set_state(SetupFSM.setup_password)

            await message.delete()

            bot_msg = await message.answer(
                "Войдите для начала работы.\nP.S Пароль единоразовый для одного аккаунта\nВведите пароль:")

            await state.update_data(bot_msg=bot_msg.message_id)
        else:
            bot_msg = await message.answer(
                "Пароля - не существует, видимо, администратор уже существует\nВведите команду и пароль заново")

            await state.update_data(bot_msg=bot_msg.message_id)

    async def setup_from_password_handler(self, message: Message, state: FSMContext):
        msg_id = await state.get_value("bot_msg")
        if message.text:
            password = await self.admin_database.select_password_try(message.text)

            if password:

                await message.delete()
                await self.admin_database.update_admin_password(str(message.chat.id))

                msg_bot_two = await message.answer(
                    "Пароль - верный, вы зарегистрированы. Пароль - теперь недействителен\n\n"
                    "Введите /add_channel")
            else:
                msg_bot_two = await message.answer("Пароль - неверный\nВведите команду и пароль заново")
        else:
            msg_bot_two = await message.answer("Это сообщение не текст\nВведите команду и пароль заново")

        await bot.delete_message(chat_id=message.chat.id, message_id=int(msg_id))
        await state.clear()
        await asyncio.sleep(30)
        await bot.delete_message(chat_id=message.chat.id, message_id=int(msg_bot_two.message_id))

    async def add_new_course(self, message: Message, state: FSMContext):
        keyboard = await self.begin_fabric_keyboard.inline_course_button()
        await message.delete()
        await state.set_state(SetupStates.none_state)
        await message.answer("Перед тем, как добавить курс. Заполните все данные по анкете ниже\n"
                                   "<pre>"
                                   f"Имя: нет\n"
                                   f"Описание: нет\n"
                                   f"Цена: нет\n"
                                   f"Айди канала: нет"
                                   "</pre>", reply_markup=keyboard)

    async def edit_course(self, callback: CallbackQuery, callback_data: CallbackData, state: FSMContext):
        msg_add_course = None
        match callback_data.action:
            case "edit_name":
                await state.set_state(SetupStates.name)
                msg_add_course = await callback.message.edit_text("Введите имя курса")

            case "edit_description":
                await state.set_state(SetupStates.description)
                msg_add_course = await callback.message.edit_text("Введите описание курса")

            case "edit_price":
                await state.set_state(SetupStates.price)
                msg_add_course = await callback.message.edit_text("Введите цену этого курса в рублях")

            case "edit_channel":
                await state.set_state(SetupStates.channel)
                msg_add_course = await callback.message.edit_text("Введите id канала")

            case "Accept":

                try:
                    try:
                        try:
                            data_course = await state.get_data()

                            name = data_course["course_name"]
                            description = data_course["course_description"]
                            price = data_course["course_price"]
                            channel_id = data_course["course_channel"]
                            if len(name) > 55:
                                await callback.answer("Название слишком большое\nДлинна больше 55", show_alert=True)
                                return

                            if len(description) > 255:
                                await callback.answer("Описание слишком большое\nДлинна больше 255", show_alert=True)
                                return

                            if int(price) < 10:
                                await callback.answer("Курс не может стоить меньше 10 рублей", show_alert=True)
                                return

                            await self.admin_database.insert_new_course(name, description, int(price), channel_id)

                            await callback.message.delete()
                            return
                        except DataError:
                            await callback.answer("Цена курса слишком большая", show_alert=True)
                    except UniqueViolationError:
                        await callback.answer("Курс с таким именем уже существует", show_alert=True)
                except KeyError:
                    await callback.answer("Вы ввели не все данные", show_alert=True)
            case _:
                msg_add_course = await callback.answer("Ошибка")
        await state.update_data(msg_add_course=msg_add_course)

        await callback.answer()

    async def edit_komponent_course(self, message: Message,  state: FSMContext):

        msg = None

        if message.text:
            last_state = await state.get_state()
            msg_add_course: Message = await state.get_value("msg_add_course")
            if last_state == SetupStates.name:
                await state.update_data(course_name=message.text)

            elif last_state == SetupStates.description:
                await state.update_data(course_description=message.text)

            elif last_state == SetupStates.price:
                try:
                    await state.update_data(course_price=int(message.text))

                except ValueError:
                    msg = await message.answer("Ваша цена - не число")


            elif last_state == SetupStates.channel:
                await state.update_data(course_channel=message.text)


            name = await state.get_value("course_name")
            description = await state.get_value("course_description")
            price = await state.get_value("course_price")
            channel_id = await state.get_value("course_channel")

            await state.set_state(SetupStates.none_state)
            keyboard = await self.begin_fabric_keyboard.inline_course_button()
            await message.delete()
            await msg_add_course.edit_text("Перед тем, как добавить курс. Заполните все данные по анкете ниже\n"
                                           "<pre>"
                                           f"Имя: {name if name else "нет"}\n"
                                           f"Описание: {description if description else "нет"}\n"
                                           f"Цена: {price if price else "нет"}\n"
                                           f"Айди канала: {channel_id if channel_id else "нет"}"
                                           "</pre>",
                                            reply_markup=keyboard)
            if msg:
                await asyncio.sleep(10)
                await msg.delete()

    async def deactivare_course(self, message: Message,):

    async def chat_id_handler(self, message: Message):
        await message.delete()
        msg = await message.answer(f"Айди чата: <pre>{message.chat.id}</pre>\n\n"
                             f"У вас минута на копирование")
        await asyncio.sleep(60)
        await msg.delete()
