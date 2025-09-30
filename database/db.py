from typing import Union, Optional

import asyncpg

from config import HOST, PASSWORD, DATABASE, USER

pg_host = HOST
pg_user = USER
pg_password = PASSWORD
pg_database = DATABASE


class Sqlbase:

    def __init__(self, pool=None):
        self.pool = pool

    async def connect(self):
        try:
            self.pool = await asyncpg.create_pool(
                host=pg_host,
                user=pg_user,
                password=pg_password,
                database=pg_database,
                min_size=1,
                max_size=10000
            )
        except Exception as e:
            print(f"Ошибка подключения к базе данных: {e}")
            raise

    async def close(self):
        if self.pool:
            await self.pool.close()

    async def execute_query(self, query, params=None) -> Union[tuple, int]:

        if not self.pool:
            raise ValueError("Пул соединений не создан. Убедитесь, что вызвали connect().")

        try:
            async with self.pool.acquire() as connection:
                async with connection.transaction():
                    if params:
                        return await connection.fetch(query, *params)
                    return await connection.fetch(query)
        except asyncpg.PostgresError as e:
            print(f"Ошибка выполнения запроса: {e}")
            raise

