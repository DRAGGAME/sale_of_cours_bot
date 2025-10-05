from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


class KeyboardFactory:
    """
    Основной класс для создания клавиатур
    """

    def __init__(self):
        self.builder_reply = None

        self.builder_inline = None

    async def create_builder_inline(self) -> None:
        self.builder_inline = InlineKeyboardBuilder()


