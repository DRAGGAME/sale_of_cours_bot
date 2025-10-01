from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import KeyboardButton, InlineKeyboardButton
import numpy as np
from config import bot
from database.user_operation import UserOperation
from keyboards.fabirc_kb import KeyboardFactory
from functions.courses import select_courses

class ChoiceCallback(CallbackData, prefix="Accept_politics"):
    accept: bool


class ChoiceCourse(CallbackData, prefix="choice_course"):
    number_course_id: Optional[int]
    page: Optional[int]
    action: Optional[str]


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

    async def inline_choice_course_keyboard(self, courses: list, page: int):
        await self.create_builder_inline()

        for course in courses[0]:
            button_course = InlineKeyboardButton(
                text=f"{course[1]}",
                callback_data=ChoiceCourse(
                    number_course_id=course[0],
                    page=page,
                    action=None
                ).pack()
            )
            self.builder_inline.row(button_course)

        back_button = InlineKeyboardButton(
            text="Назад",
            callback_data=ChoiceCourse(
                number_course_id=None,
                page=page,
                action="back"
            ).pack()
        )

        next_button = InlineKeyboardButton(
            text="Вперёд",
            callback_data=ChoiceCourse(
                number_course_id=None,
                page=page,
                action="next"
            ).pack()
        )

        self.builder_inline.row(back_button, next_button)
        return self.builder_inline.as_markup()

    async def inline_back_button(self):
        await self.create_builder_inline()

        back_button = InlineKeyboardButton(
            text="Назад",
            callback_data=ChoiceCallback(
                accept=True,
            ).pack()
        )

        self.builder_inline.add(back_button)
        return self.builder_inline.as_markup()



