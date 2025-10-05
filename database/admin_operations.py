from typing import List

from database.user_operation import UserOperation


class AdminOperation(UserOperation):

    async def insert_new_user(self, chat_id: str):
        await self.execute_query("""
        INSERT INTO user_data (chat_id) VALUES ($1);
        """, (chat_id,))

    async def insert_new_transaction(self, chat_id: str, name_transaction, transaction_id, amount):
        await self.execute_query("""INSERT INTO all_transaction (chat_id, name_transaction, transaction_id, amount)
                                    VALUES ($1, $2, $3, $4);""", (chat_id, name_transaction, transaction_id, amount))

    async def select_password_and_user(self) -> tuple:
        password_admin = await self.execute_query("""SELECT password_admin, admin_chat_id
                                                     FROM settings_table""")
        return password_admin[0]

    async def select_password_try(self, password: str) -> tuple:
        password = await self.execute_query("""
                                        SELECT password_admin = crypt($1, password_admin) FROM settings_table;
                                        """, (password, ))
        return password

    async def update_admin_password(self, admin_chat_id: str) -> None:
        await self.execute_query("""UPDATE settings_table
                                    SET password_admin=$1,
                                        admin_chat_id=$2""",
                                 (None, admin_chat_id))

    async def insert_new_course(self, name: str, description: str, price: int, channel_id: str) -> None:
        await self.execute_query("""INSERT INTO courses (name, price, channel_id, description) VALUES ($1, $2, $3, $4);"""
                                 , (name, price, channel_id, description, ))

    async def select_all_f_and_t_courses(self) -> List[List]:
        raw_data = await self.execute_query("SELECT * FROM courses ORDER BY id ASC;")

        data_a_courses: list = [raw_data[i:i + 2] for i in range(0, len(raw_data), 2)]

        return data_a_courses

    async def update_status(self, id: str, status: bool):
        status = await self.execute_query("""UPDATE courses SET status = $1 WHERE id = $2
                                        RETURNING status;""", (status, id))
        return status

    async def check_count_courses(self):
        data = await self.execute_query("""
        SELECT 
        COUNT(*) FILTER (WHERE date_pay >= NOW() - INTERVAL '7 days') AS courses_bought_week,
        SUM(amount / 100) AS total_earned
        FROM all_transaction;
        """)
        return data[0]

    async def update_url_politic(self, type_politic: str, url_politic: str):
        if type_politic == "kond":
            await self.execute_query("""UPDATE settings_table SET kond_politics = $1""", (url_politic, ))
        else:
            await self.execute_query("""UPDATE settings_table SET user_politics = $1""", (url_politic, ))