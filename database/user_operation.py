from typing import Tuple, List, Union, Optional, Any, Coroutine

from database.db import Sqlbase


class UserOperation(Sqlbase):

    async def select_main_message(self) -> str:

        main_message = await self.execute_query("""SELECT main_message FROM settings_table;""")

        return main_message[0][0]

    async def select_all_courses(self, main_handlers: bool) -> tuple[list, list | None]:
        """
        Выборка и создание данных по-парно
        :return:
        :rtype: List[List]

        """
        if main_handlers:
            raw_data, main_message = await self.execute_transaction(
                [("SELECT * FROM courses WHERE status=True ORDER BY id ASC;", None),
                 ("SELECT main_message FROM settings_table;", None)])
            main_message = main_message[0][0]
        else:
            raw_data = await self.execute_query("SELECT * FROM courses WHERE status=True ORDER BY id ASC;")
            main_message = None

        data_list = [tuple(record) for record in raw_data]

        data_a_courses: list = [data_list[i:i + 2] for i in range(0, len(data_list), 2)]

        return data_a_courses, main_message

    async def select_user(self, chat_id: str) -> bool:
        """
        Данные пользователя по chat_id
        :param chat_id:
        :return:
        """
        status = await self.execute_query("""SELECT * FROM user_data WHERE chat_id = $1;""", (chat_id, ))

        if bool(status):
            return True
        else:
            return False

    async def select_course(self, id_course: int) -> Tuple:
        """
        Извлекаем курс по айди
        :param id_course:
        :return:
        """
        course_data = await self.execute_query("""SELECT * FROM courses WHERE id = $1;""", (id_course, ))
        return course_data[0]

    async def select_admin_chat(self) -> str:
        """
        Извлечение админского айди
        :return:
        """
        admin_chat = await self.execute_query("""SELECT admin_chat_id FROM settings_table""")

        return admin_chat[0][0]