from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.fabirc_kb import KeyboardFactory


class PayCourse(CallbackData, prefix="pay_prefix"):
    action: str
    price: Optional[int]


class ChoiceCallback(CallbackData, prefix="Accept_politics"):
    accept: bool


class ChoiceCourse(CallbackData, prefix="choice_course"):
    number_course_id: Optional[int]
    page: Optional[int]
    action: Optional[str]


class FabricInline(KeyboardFactory):
    """
    ПОльзовательские клавиатуры
    """

    def __init__(self):
        super().__init__()

    async def inline_choice_course_keyboard(self, courses: list, page: int) -> InlineKeyboardMarkup:
        """
        По-парное создание кнопок для курсов
        :param courses:
        :param page:
        :return:
        """
        await self.create_builder_inline()

        for course in courses[page]:
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

    async def inline_pay_keyboard(self, price: int) -> InlineKeyboardMarkup:
        """
        Покупка курса
        :param price:
        :return:
        """
        await self.create_builder_inline()
        pay_button = InlineKeyboardButton(
            text=f"Купить за {price}",
            callback_data=PayCourse(
                action="pay",
                price=price,
            ).pack()
        )
        back_button = InlineKeyboardButton(
            text="Назад",
            callback_data=ChoiceCallback(
                accept=True,
            ).pack()
        )
        self.builder_inline.add(pay_button)
        self.builder_inline.row(back_button)
        return self.builder_inline.as_markup()

    async def payment_create_kb(self, price: int):
        """
        Покупка курса, окончательная
        :param price:
        :return:
        """
        await self.create_builder_inline()

        pay = InlineKeyboardButton(
            text=f"Оплатить {price} RUB",
            pay=True,
        )

        button_back = InlineKeyboardButton(
            text="Отмена платежа",
            callback_data=PayCourse(
                action="cancel_payment",
                price=None,
            ).pack()
        )

        self.builder_inline.add(pay)
        self.builder_inline.row(button_back)

        return self.builder_inline.as_markup()
