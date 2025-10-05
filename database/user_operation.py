from typing import Tuple, List

from database.db import Sqlbase


class UserOperation(Sqlbase):

    async def select_all_courses(self) -> List[List]:
        """
        Выборка и создание данных по-парно
        :return:
        :rtype: List[List]
        """
        raw_data = await self.execute_query("SELECT * FROM courses WHERE status=True ORDER BY id ASC;")

        data_a_courses: list = [raw_data[i:i + 2] for i in range(0, len(raw_data), 2)]

        return data_a_courses

    async def select_politics(self) -> Tuple[str, str]:
        """
        Пользовательское соглашение
        :return:
        """
        politics: Tuple[Tuple[str, str]] = await self.execute_query("""SELECT user_politics, kond_politics FROM settings_table;""")
        return politics[0]

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