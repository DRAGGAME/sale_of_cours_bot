from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton

from keyboards.fabirc_kb import KeyboardFactory


class StopInline(CallbackData, prefix="stop"):
    action: str


class AdminChoiceCourse(CallbackData, prefix="choice_course_admin"):
    number_course_id: Optional[int]
    page: Optional[int]
    action: Optional[str]


class AdminFabric(KeyboardFactory):
    def __init__(self):
        super().__init__()

    async def inline_course_button(self):
        await self.create_builder_inline()

        button_name = InlineKeyboardButton(
            text="Имя",
            callback_data=StopInline(
                action="edit_name"
            ).pack()
        )

        button_description = InlineKeyboardButton(
            text="Описание",
            callback_data=StopInline(
                action="edit_description"
            ).pack()
        )

        button_price = InlineKeyboardButton(
            text="Цена",
            callback_data=StopInline(
                action="edit_price"
            ).pack()
        )

        button_channel = InlineKeyboardButton(
            text="Канал",
            callback_data=StopInline(
                action="edit_channel"
            ).pack()
        )

        button_accept = InlineKeyboardButton(
            text="Готово",
            callback_data=StopInline(
                action="Accept"
            ).pack()
        )

        button_stop = InlineKeyboardButton(
            text="Остановить",
            callback_data=StopInline(
                action="stop"
            ).pack()
        )
        self.builder_inline.add(button_name, button_description, button_channel, button_price)
        self.builder_inline.row(button_accept)
        self.builder_inline.row(button_stop)

        return self.builder_inline.as_markup()

    async def inline_activate_or_deac_course(self, courses: list, page: int):
        await self.create_builder_inline()

        for course in courses[page]:
            button_course = InlineKeyboardButton(
                text=f"{course[1]}",
                callback_data=AdminChoiceCourse(
                    number_course_id=course[0],
                    page=page,
                    action=None
                ).pack()
            )
            self.builder_inline.row(button_course)

        back_button = InlineKeyboardButton(
            text="Назад",
            callback_data=AdminChoiceCourse(
                number_course_id=None,
                page=page,
                action="back"
            ).pack()
        )

        next_button = InlineKeyboardButton(
            text="Вперёд",
            callback_data=AdminChoiceCourse(
                number_course_id=None,
                page=page,
                action="next"
            ).pack()
        )

        self.builder_inline.row(back_button, next_button)
        return self.builder_inline.as_markup()

    async def choice_course_admin(self):
        await self.create_builder_inline()
