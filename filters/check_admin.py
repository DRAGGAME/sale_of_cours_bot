from typing import Union

from aiogram.filters import BaseFilter

from database.admin_operations import UserOperation

from aiogram.types import Message, CallbackQuery

from logger import logger


# from logger import logger


class CheckRegistryUser(BaseFilter):

    def __init__(self, sqlbase: UserOperation):
        self.sqlbase = sqlbase

    async def __call__(self, message_or_callback: Union[Message, CallbackQuery]) -> bool:

        if isinstance(message_or_callback, Message):
            user = await self.sqlbase.select_user(str(message_or_callback.chat.id))
        else:
            user = await self.sqlbase.select_user(str(message_or_callback.message.chat.id))
        if not user:
            return True
        else:
            return False


class CheckSelectUser(BaseFilter):
    def __init__(self, sqlbase: UserOperation):
        self.sqlbase = sqlbase

    async def __call__(self, message: Message) -> bool:
        user = await self.sqlbase.select_user(str(message.chat.id))
        if user:
            return True
        else:
            return False