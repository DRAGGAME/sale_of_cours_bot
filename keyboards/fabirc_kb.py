from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


class KeyboardFactory:

    def __init__(self):
        self.builder_reply = None

        self.builder_inline = None

    async def create_builder_reply(self) -> None:
        self.builder_reply = ReplyKeyboardBuilder()

    async def create_builder_inline(self) -> None:
        self.builder_inline = InlineKeyboardBuilder()

    async def builder_reply_choice(self, text_input: str) -> ReplyKeyboardMarkup:
        await self.create_builder_reply()
        self.builder_reply.add(KeyboardButton(text="Да✅"))
        self.builder_reply.add(KeyboardButton(text="Нет❌"))

        keyboard = self.builder_reply.as_markup(
            resize_keyboard=True,
            input_field_placeholder=text_input, one_time_keyboard=True)
        return keyboard

