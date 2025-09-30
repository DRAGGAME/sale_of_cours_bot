from aiogram.filters.callback_data import CallbackData
from aiogram.types import KeyboardButton, InlineKeyboardButton

from keyboards.fabirc_kb import KeyboardFactory


class ChoiceCallback(CallbackData, prefix="Accept_politics"):
    accept: bool


class FabricInline(KeyboardFactory):

    def __init__(self):
        super().__init__()

    async def inline_choice_keyboard(self):
        await self.create_builder_inline()

        yes_button = InlineKeyboardButton(
            text="Принять",
            callback_data=ChoiceCallback(
                accept=True,
            ).pack()
        )

        no_button = InlineKeyboardButton(
            text="Отказаться",
            callback_data=ChoiceCallback(
                accept=False,
            ).pack()
        )

        self.builder_inline.add(yes_button)
        self.builder_inline.add(no_button)
        return self.builder_inline.as_markup()
