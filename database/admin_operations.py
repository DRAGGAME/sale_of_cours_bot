from typing import List

from database.user_operation import UserOperation


class AdminOperation(UserOperation):
    """
    Админский класс, сочетает в себе вставки и апдейты и, издредко, выборку данных
    """
    async def insert_new_user(self, chat_id: str):
        """
        Новый пользователь
        :param chat_id:
        :return:
        """
        await self.execute_query("""
        INSERT INTO user_data (chat_id) VALUES ($1);
        """, (chat_id,))

    async def insert_new_transaction(self, chat_id: str, name_transaction, transaction_id, amount):
        """
        При новой транзакции, обязателен chat_id из user_data
        :param chat_id:
        :param name_transaction:
        :param transaction_id:
        :param amount:
        :return:
        """
        await self.execute_query("""INSERT INTO all_transaction (chat_id, name_transaction, transaction_id, amount)
                                    VALUES ($1, $2, $3, $4);""", (chat_id, name_transaction, transaction_id, amount))

    async def select_password_and_user(self) -> tuple:
        """
        Данные, что существует пароль
        :return:
        """
        password_admin = await self.execute_query("""SELECT password_admin, admin_chat_id
                                                     FROM settings_table""")
        return password_admin[0]

    async def select_password_try(self, password_admin: str) -> tuple:
        """
        Проверка хэша пароля
        :param password_admin:
        :return:
        """
        password_admin = await self.execute_query("""
                                        SELECT password_admin = crypt($1, password_admin) FROM settings_table;
                                        """, (password_admin, ))
        return password_admin

    async def update_admin_password(self, admin_chat_id: str) -> None:
        """
        Изменение пароля админа на None
        :param admin_chat_id:
        :return:
        """
        await self.execute_query("""UPDATE settings_table SET (password_admin, admin_chat_id)=($1, $2) """, (None, admin_chat_id))

    async def insert_new_course(self, name: str, description: str, price: int, channel_id: str) -> None:
        """
        Вставка нового курса
        :param name:
        :param description:
        :param price:
        :param channel_id:
        :return:
        """
        await self.execute_query("""INSERT INTO courses (name, price, channel_id, description) VALUES ($1, $2, $3, $4);"""
                                 , (name, price, channel_id, description, ))

    async def select_all_f_and_t_courses(self) -> List[List]:
        """
        Извлечение всех курсов
        :return:
        """
        raw_data = await self.execute_query("SELECT * FROM courses ORDER BY id ASC;")

        data_list = [tuple(record) for record in raw_data]

        data_a_courses: list = [data_list[i:i + 2] for i in range(0, len(data_list), 2)]

        return data_a_courses

    async def update_status(self, id: str, status: bool):
        """
        Изменение статуса курса
        :param id:
        :param status:
        :return:
        """
        status = await self.execute_query("""UPDATE courses SET status = $1 WHERE id = $2
                                        RETURNING status;""", (status, id))
        return status

    async def check_count_courses(self):
        """
        Выборка, сколько продано курсов за 7 дней, и сумма проданных всего за 7 дней
        :return:
        """
        data = await self.execute_query("""
        SELECT 
        COUNT(*) FILTER (WHERE date_pay >= NOW() - INTERVAL '7 days') AS courses_bought_week,
        SUM(amount / 100) AS total_earned
        FROM all_transaction;
        """)
        return data[0]

    async def update_main_message(self, main_message: str):
        """
        Апдейт политик
        :param main_message:
        :return:
        """
        await self.execute_query("""UPDATE settings_table SET main_message = $1""", (main_message, ))
