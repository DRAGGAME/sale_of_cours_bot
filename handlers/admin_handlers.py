import asyncio

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from asyncpg import UniqueViolationError, DataError

from config import bot
from database.admin_operations import AdminOperation
from filters.check_admin import CheckAdmin, CheckAdminSetup
from keyboards.admin_fabric import AdminFabric, StopInline, AdminChoiceCourse, BeginPage, MainMenu, UpdatePoliticInline


class SetupStates(StatesGroup):
    name = State()
    description = State()
    price = State()
    channel = State()
    none_state = State()


class SetupFSM(StatesGroup):
    setup_password = State()


class SetupMainMessage(SetupStates):
    edit_main_message = State()


class AdminHandlers:

    def __init__(self):
        self.bot = bot
        self.router = Router()
        self.admin_database = AdminOperation()
        self.admin_fabric_inline = AdminFabric()

        self.register_handlers_is_admin()

    def register_handlers_is_admin(self):

        self.router.message.register(self.admin_call, Command(commands=["admin", "Admin"]),
                                     CheckAdmin(self.admin_database))
        self.router.callback_query.register(self.back_panel_handler, MainMenu.filter(F.action == "main_menu"))

        self.router.channel_post.register(self.chat_id_handler, Command("chat_id"))

        self.router.message.register(self.setup_handler, CheckAdminSetup(self.admin_database), Command("setup"))
        self.router.message.register(self.setup_from_password_handler, SetupFSM.setup_password,
                                     CheckAdminSetup(self.admin_database))

        self.router.callback_query.register(self.add_new_course, MainMenu.filter(F.action == "add_course"))
        self.router.callback_query.register(self.edit_course, StopInline.filter(F.action), SetupStates.none_state)
        self.router.message.register(self.edit_komponent_course, F, SetupStates.name)
        self.router.message.register(self.edit_komponent_course, F, SetupStates.description)
        self.router.message.register(self.edit_komponent_course, F, SetupStates.price)
        self.router.message.register(self.edit_komponent_course, F, SetupStates.channel)

        self.router.callback_query.register(self.deactivate_course, MainMenu.filter(F.action == "status_course"))
        self.router.callback_query.register(self.deactivate_course, BeginPage.filter(F.back == True))
        self.router.callback_query.register(self.action_course, AdminChoiceCourse.filter(F.number_course_id != None))
        self.router.callback_query.register(self.choice_page_admin, AdminChoiceCourse.filter(F.action != None))
        self.router.callback_query.register(self.end_activate_or_deactivate,
                                            BeginPage.filter(F.number_course_id != None))

        self.router.callback_query.register(self.data_a_pay_course, MainMenu.filter(F.action == "data_a_course"))

        self.router.callback_query.register(self.main_message_handler, MainMenu.filter(F.action == "edit_main_message"))
        self.router.message.register(self.edit_main_message, F, SetupMainMessage.edit_main_message)

        self.router.callback_query.register(self.delete_profile_admin, MainMenu.filter(F.action == "clear_settings"))

    async def admin_call(self, message: Message, state: FSMContext):
        await state.clear()
        admin_keyboard = await self.admin_fabric_inline.main_menu_admin()
        await message.delete()
        await message.answer("Приветсвую вас в админ-панели\n\n"
                             "Что вы хотите сделать?", reply_markup=admin_keyboard)

    async def back_panel_handler(self, callback: CallbackQuery, state: FSMContext):
        await state.clear()
        admin_keyboard = await self.admin_fabric_inline.main_menu_admin()
        await callback.message.edit_text("Все параметры сброшены.\n\n"
                                         "Что вы хотите сделать?", reply_markup=admin_keyboard)

    async def add_new_course(self, callback: CallbackQuery, state: FSMContext):
        keyboard = await self.admin_fabric_inline.inline_course_button()
        await state.set_state(SetupStates.none_state)
        await callback.message.edit_text("Перед тем, как добавить курс. Заполните все данные по анкете ниже\n"
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
                            if int(price) < 10:
                                await callback.answer("Курс не может стоить меньше 10 рублей", show_alert=True)
                                return

                            await self.admin_database.insert_new_course(name, description, int(price), channel_id)
                            back_panel = await self.admin_fabric_inline.default_back_in_panel()
                            await callback.message.edit_text("Курс создан с парметрами"
                                                             "<pre>"
                                                             f"Имя: {name}\n"
                                                             f"Описание: {description}\n"
                                                             f"Цена: {price}\n"
                                                             f"Айди канала: {channel_id}"
                                                             "</pre>", reply_markup=back_panel)

                            return

                        except DataError:
                            await callback.answer("Цена курса слишком большая", show_alert=True)
                    except UniqueViolationError:
                        await callback.answer("Курс с таким именем уже существует", show_alert=True)
                except KeyError:
                    await callback.answer("Вы ввели не все данные", show_alert=True)
            case "stop":
                await state.clear()
                await callback.answer("Вы остановили создание нового курса", show_alert=True)
                return

            case _:
                msg_add_course = await callback.answer("Ошибка", show_alert=True)
        await state.update_data(msg_add_course=msg_add_course)

        await callback.answer()

    async def edit_komponent_course(self, message: Message, state: FSMContext):

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
                    price = message.text
                    price = price.replace(" ", "")
                    price = price.replace(",", "")
                    price = price.replace(".", "")
                    await state.update_data(course_price=int(price))

                except ValueError:
                    msg = await msg_add_course.answer("Ваша цена - не число", show_alert=True)

            elif last_state == SetupStates.channel:
                await state.update_data(course_channel=message.text)

            name = await state.get_value("course_name")
            description = await state.get_value("course_description")
            price = await state.get_value("course_price")
            channel_id = await state.get_value("course_channel")

            await state.set_state(SetupStates.none_state)
            keyboard = await self.admin_fabric_inline.inline_course_button()
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

    async def deactivate_course(self, callback: CallbackQuery, state: FSMContext) -> None:
        data_courses = await self.admin_database.select_all_f_and_t_courses()
        await state.update_data(data_courses=data_courses)
        if data_courses:
            keyboard = await self.admin_fabric_inline.inline_activate_or_deac_course(data_courses, page=0)
            await callback.message.edit_text("Нажмите 1 раз для подробностей о курсе, "
                                             "второй раз для деактивации или активации курса",
                                             reply_markup=keyboard)
        else:
            kb_main = await self.admin_fabric_inline.main_menu_admin()
            await callback.message.edit_text(
                "Похоже, у вас нет курсов. Добавьте их в главном меню", reply_markup=kb_main)

    async def action_course(self, callback: CallbackQuery, callback_data: CallbackData, state: FSMContext):
        number_course_id: int = callback_data.number_course_id
        course = await self.admin_database.select_course(int(number_course_id))

        await state.update_data(data_course=tuple(course))
        keyboard_back = await self.admin_fabric_inline.inline_back_keyboard(course[-1], course[0])
        await callback.message.edit_text(f"<pre>"
                                         f"Название курса: {course[1]}"
                                         f"\nОписание курса: {course[-2]}"
                                         f"\nЦена курса: {course[-4]}"
                                         f"\nАктивирован: {'да' if course[-1] else 'нет'}"
                                         f"</pre>", reply_markup=keyboard_back)
        await callback.answer()

    async def choice_page_admin(self, callback: CallbackQuery, callback_data: CallbackData, state: FSMContext):
        page = callback_data.page
        action = callback_data.action
        all_courses = await state.get_value("data_courses")
        if action == "next" and page < len(all_courses) - 1:
            page += 1
        elif action == "back" and page > 0:
            page -= 1
        else:
            await callback.answer("Дальше курсов нет", show_alert=True)
            return

        kb = await self.admin_fabric_inline.inline_activate_or_deac_course(all_courses, page)

        await callback.message.edit_text("Выберите курс", reply_markup=kb)
        await callback.answer()

    async def end_activate_or_deactivate(self, callback: CallbackQuery, callback_data: CallbackData, state: FSMContext):
        next_status = callback_data.next_status
        id_course = callback_data.number_course_id

        text = callback.message.text
        end_text_status = text.split(sep="\n")[-1].split(sep=":")[1].replace(" ", "")

        if end_text_status == "нет":
            end_text_status_new = "да"
        else:
            end_text_status_new = "нет"

        form_string = f"Активирован: {end_text_status_new}"
        new_text = text.replace(f"Активирован: {end_text_status}", form_string)

        await self.admin_database.update_status(id_course, next_status)
        keyboard = await self.admin_fabric_inline.inline_back_keyboard(status=next_status, id_course=id_course)
        await state.clear()
        await callback.message.edit_text(f"<pre>{new_text}</pre>", reply_markup=keyboard)
        await callback.answer()

    async def data_a_pay_course(self, callback: CallbackQuery):
        data = await self.admin_database.check_count_courses()
        back_panel = await self.admin_fabric_inline.default_back_in_panel()
        if data[1]:
            await callback.message.edit_text(f"Сколько купили курсов за неделю: {data[0]}"
                                             f"\nСколько вы заработали без вычетов каких-либо процентов: {data[1]}",
                                             reply_markup=back_panel)
        else:
            await callback.message.edit_text("В течение недели не было продано ни единого курса",
                                             reply_markup=back_panel)

    async def main_message_handler(self, callback: CallbackQuery, state: FSMContext):

        await state.set_state(SetupMainMessage.edit_main_message)
        msg_main = await callback.message.edit_text("Введите приветственное сообщение")
        await state.update_data(msg_main=msg_main)
        await callback.answer()

    async def edit_main_message(self, message: Message, state: FSMContext):
        msg_main: Message = await state.get_value("msg_main")
        await self.admin_database.update_main_message(message.text)
        back_panel = await self.admin_fabric_inline.default_back_in_panel()

        await state.clear()

        await message.delete()
        await msg_main.edit_text(f"Вы успешно изменили приветственное сообщение на: \n\n{message.text}", reply_markup=back_panel)


    async def setup_handler(self, message: Message, state: FSMContext):
        password_admin = await self.admin_database.select_password_and_user()
        await state.clear()

        if password_admin:
            await message.delete()

            await state.set_state(SetupFSM.setup_password)

            bot_msg = await message.answer(
                "Войдите для начала работы.\nP.S Пароль единоразовый для одного аккаунта\nВведите пароль:")

            await state.update_data(bot_msg=bot_msg.message_id)
        else:
            bot_msg = await message.answer(
                "Пароля - не существует, видимо, администратор уже существует\nВведите команду и пароль заново")

            await asyncio.sleep(60)
            await bot_msg.delete()

    async def setup_from_password_handler(self, message: Message, state: FSMContext):
        msg_id = await state.get_value("bot_msg")
        await bot.delete_message(chat_id=message.chat.id, message_id=int(msg_id))

        if message.text:
            password_admin = await self.admin_database.select_password_try(message.text)
            if password_admin[0][0]:

                await message.delete()
                await self.admin_database.update_admin_password(str(message.chat.id))
                admin_keyboard = await self.admin_fabric_inline.main_menu_admin()

                msg_bot_two = await message.answer(
                    "Пароль - верный, вы зарегистрированы. Пароль - теперь недействителен\n\nЧто вы хотите сделать",
                    reply_markup=admin_keyboard)
                await state.clear()

                return

            else:
                msg_bot_two = await message.answer("Пароль - неверный\nВведите команду и пароль заново")
                await state.clear()

                await asyncio.sleep(30)
                await bot.delete_message(chat_id=message.chat.id, message_id=int(msg_bot_two.message_id))
        else:
            msg_bot_two = await message.answer("Это сообщение не текст\nВведите команду и пароль заново")
            await state.clear()

            await asyncio.sleep(30)
            await bot.delete_message(chat_id=message.chat.id, message_id=int(msg_bot_two.message_id))

    async def chat_id_handler(self, message: Message):
        await message.delete()
        msg = await message.answer(f"Айди чата: <code>{message.chat.id}</code>\n\n"
                                   f"У вас минута на копирование")
        await asyncio.sleep(60)
        await msg.delete()

    async def delete_profile_admin(self, callback: CallbackQuery):
        from database.create_table import CreateTable
        sqlbase_table = CreateTable()

        await sqlbase_table.delete_settings_table_table()
        await sqlbase_table.create_settings_table()

        await callback.message.edit_text("Данные администратора сброшены. Введите /setup для начала регистрации",
                                         show_alert=True)
        await asyncio.sleep(20)
        await callback.message.delete()
