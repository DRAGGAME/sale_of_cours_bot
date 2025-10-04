import asyncio

import apscheduler
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from config import bot
from database.admin_operations import AdminOperations
from filters.check_admin_for_setup import CheckAdminSetup


from keyboards.menu_fabric import FabricInline
router_for_user = Router()
sqlbase_for_admin_function = AdminOperations()
keyboard = FabricInline()


class SetupFSM(StatesGroup):
    setup_password = State()

@router_for_user.message(CommandStart(), CheckAdminSetup(sqlbase_for_admin_function))
@router_for_user.message(Command(commands=["setup", "Setup"]), CheckAdminSetup(sqlbase_for_admin_function))


class

async def setup_handler(message: Message, state: FSMContext):
    await sqlbase_for_admin_function.connect()
    password = await sqlbase_for_admin_function.select_password_and_user()
    await state.clear()

    if password:
        await state.set_state(SetupFSM.setup_password)

        await message.delete()

        bot_msg = await message.answer("Войдите для начала работы.\nP.S Пароль единоразовый для одного аккаунта\nВведите пароль:")

        await state.update_data(password=password[0], bot_msg=bot_msg.message_id)
    else:
        bot_msg = await message.answer("Пароля - не существует, видимо, администратор уже существует\nВведите команду и пароль заново")

        await state.update_data(bot_msg=bot_msg.message_id)

async def setup_from_password_handler(message: Message, state: FSMContext):
    msg_id = await state.get_value("bot_msg")
    if message.text:
        password = await state.get_value("password")

        if message.text == password:

            await message.delete()
            await sqlbase_for_admin_function.update_admin_password(str(message.chat.id))

            msg_bot_two = await message.answer("Пароль - верный, вы зарегистрированы. Пароль - теперь недействителен\n\n"
                                               "Введите /start")
        else:
            msg_bot_two = await message.answer("Пароль - неверный\nВведите команду и пароль заново")
    else:
        msg_bot_two = await message.answer("Это сообщение не текст\nВведите команду и пароль заново")

    await bot.delete_message(chat_id=message.chat.id, message_id=int(msg_id))
    await state.clear()
    await sqlbase_for_admin_function.close()
    await asyncio.sleep(30)
    await bot.delete_message(chat_id=message.chat.id, message_id=int(msg_bot_two.message_id))





