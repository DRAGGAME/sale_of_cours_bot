from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.fabirc_kb import KeyboardFactory


class MainMenu(CallbackData, prefix="main_menu"):
    action: str


class StopInline(CallbackData, prefix="stop"):
    action: str


class AdminChoiceCourse(CallbackData, prefix="choice_course_admin"):
    number_course_id: Optional[int]
    page: Optional[int]
    action: Optional[str]


class BeginPage(CallbackData, prefix="begin_page"):
    next_status: Optional[bool]
    number_course_id: Optional[int]
    back: bool


class UpdatePoliticInline(CallbackData, prefix="update_politic_inline"):
    type_politics: str


class AdminFabric(KeyboardFactory):
    """
    Админские клавиатуры
    """
    def __init__(self):
        self.button_in_main = InlineKeyboardButton(
            text="В главное меню",
            callback_data=MainMenu(
                action="main_menu",
            ).pack()
        )

        super().__init__()

    async def main_menu_admin(self) -> InlineKeyboardMarkup:
        """
        Главная админская панель
        :return:
        """
        await self.create_builder_inline()
        button_add_course = InlineKeyboardButton(
            text="Добавить курс",
            callback_data=MainMenu(
                action="add_course",
            ).pack()
        )

        button_status_course = InlineKeyboardButton(
            text="Все курсы",
            callback_data=MainMenu(
                action="status_course",
            ).pack()
        )

        button_data_a_course = InlineKeyboardButton(
            text="Данные по продажам",
            callback_data=MainMenu(
                action="data_a_course",
            ).pack()
        )

        button_edit_main_message = InlineKeyboardButton(
            text='Изменить "главное" сообщение',
            callback_data=MainMenu(
                action="edit_main_message",
            ).pack()
        )

        button_clear_admin = InlineKeyboardButton(
            text="Сбросить админские настройки",
            callback_data=MainMenu(
                action="clear_settings",
            ).pack()

        )

        self.builder_inline.row(button_add_course, button_status_course)
        self.builder_inline.row(button_data_a_course)
        self.builder_inline.row(button_edit_main_message)
        self.builder_inline.row(button_clear_admin)

        return self.builder_inline.as_markup()

    async def inline_course_button(self) -> InlineKeyboardMarkup:
        """
        Для создания курса
        :return:
        """
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

        self.builder_inline.add(button_name, button_description, button_channel, button_price)
        self.builder_inline.row(button_accept)
        self.builder_inline.row(self.button_in_main)

        return self.builder_inline.as_markup()

    async def inline_activate_or_deac_course(self, courses: list, page: int) -> InlineKeyboardMarkup:
        """
        Для активации и деактивации курсов
        :param courses: - курсы, сделанные по-парно
        :param page: - текущая страница(взятая пара)
        :return:
        """
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
        self.builder_inline.row(self.button_in_main)
        return self.builder_inline.as_markup()

    async def inline_back_keyboard(self, status: bool, id_course: Optional[int]) -> InlineKeyboardMarkup:
        """
        Активирование и деактивирование курса
        :param status:
        :param id_course:
        :return:
        """
        await self.create_builder_inline()

        activate_button = InlineKeyboardButton(
            text=f"{'Деактивировать' if status else 'Активировать'}",
            callback_data=BeginPage(
                next_status=False if status else True,
                number_course_id=id_course,
                back=False
            ).pack()
        )

        back_button = InlineKeyboardButton(
            text="Назад",
            callback_data=BeginPage(
                next_status=None,
                number_course_id=None,
                back=True
            ).pack()
        )
        self.builder_inline.row(activate_button)
        self.builder_inline.row(back_button)

        return self.builder_inline.as_markup()

    async def default_back_in_panel(self)  -> InlineKeyboardMarkup:
        await self.create_builder_inline()

        self.builder_inline.row(self.button_in_main)
        return self.builder_inline.as_markup()
