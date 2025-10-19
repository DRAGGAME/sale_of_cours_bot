from asyncpg import DuplicateObjectError

from config import PASSWORD_ADMIN
from database.db import Sqlbase


class CreateTable(Sqlbase):

    async def init_pgcrypto(self):
        """
        Инициализация pgcrypto
        :return:
        """
        try:
            await self.execute_query("""CREATE EXTENSION pgcrypto;""")
        except DuplicateObjectError:
            pass

    async def create_accepted_users_table(self):
        """
        Пользовательские данные
        :return:
        """
        await self.execute_query("""CREATE TABLE IF NOT EXISTS user_data (
        id SERIAL PRIMARY KEY,
        chat_id TEXT UNIQUE NOT NULL);""")

    async def create_course_table(self):
        """
        Таблица с курсасм
        :return:
        """
        await self.execute_query("""CREATE TABLE IF NOT EXISTS courses (
                                    id SERIAL PRIMARY KEY,
                                    name TEXT NOT NULL,
                                    price INTEGER DEFAULT 1000,
                                    channel_id TEXT UNIQUE NOT NULL,
                                    description TEXT NOT NULL,
                                    status BOOLEAN DEFAULT TRUE)""")

    async def create_transaction_table(self):
        """
        Для транзакий
        :return:
        """
        await self.execute_query("""CREATE TABLE IF NOT EXISTS all_transaction (
        id SERIAL PRIMARY KEY,
        chat_id TEXT NOT NULL,
        name_transaction TEXT,
        date_pay TIMESTAMP WITH TIME ZONE DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'Europe/Moscow'),
        transaction_id TEXT UNIQUE NOT NULL,
        amount INTEGER NOT NULL,
        FOREIGN KEY (chat_id) REFERENCES user_data (chat_id) ON DELETE RESTRICT);""")

    async def create_settings_table(self):
        """
        Админ-таблица
        :return:
        """
        await self.execute_query("""CREATE TABLE IF NOT EXISTS settings_table(
        id SERIAL PRIMARY KEY,
        admin_chat_id TEXT DEFAULT '0',
        password_admin TEXT,
        main_message TEXT DEFAULT '0'
        );""")

        if await self.execute_query("""SELECT password_admin FROM settings_table LIMIT 1"""):
            pass
        else:
            await self.execute_query("""INSERT INTO settings_table (password_admin)
                                        VALUES (crypt($1, gen_salt('bf')));""", (PASSWORD_ADMIN, ))

    async def delete_settings_table_table(self):
        """
        Удаление таболицы настроек
        :return:
        """
        await self.execute_query("""DROP TABLE IF EXISTS public.settings_table CASCADE;""")
