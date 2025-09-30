from typing import Tuple

from database.db import Sqlbase


class UserOperation(Sqlbase):

    async def select_all_courses(self) -> tuple:
        all_courses = await self.execute_query("""SELECT * FROM courses;""")
        return all_courses

    async def select_politics(self) -> Tuple[str, str]:
        politics: Tuple[Tuple[str, str]] = await self.execute_query("""SELECT user_politics, kond_politics FROM settings_table;""")
        return politics[0]

    async def select_user(self, chat_id: str) -> bool:
        status = await self.execute_query("""SELECT * FROM user_data WHERE chat_id = $1;""", (chat_id, ))

        if bool(status):
            return True
        else:
            return False