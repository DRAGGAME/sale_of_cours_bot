from typing import Union
import asyncpg

from config import HOST, PASSWORD, DATABASE, USER

pg_host = HOST
pg_user = USER
pg_password = PASSWORD
pg_database = DATABASE

_pool: asyncpg.Pool | None = None


class Sqlbase:

    def __init__(self, pool=None):
        self.pool = pool or _pool

    @classmethod
    async def init_pool(cls, **kwargs):
        """
        Создаёт глобальный пул, который будет использоваться всеми наследниками.
        """
        global _pool
        if _pool is None:
            _pool = await asyncpg.create_pool(
                host=pg_host,
                user=pg_user,
                password=pg_password,
                database=pg_database,
                min_size=1,
                max_size=10_000,
                **kwargs
            )
        return _pool

    @classmethod
    async def close_pool(cls):
        global _pool
        if _pool:
            await _pool.close()
            _pool = None

    async def execute_query(self, query, params=None) -> Union[tuple, int]:
        if not self.pool:
            raise ValueError("Пул соединений не создан. Убедитесь, что вызвали Sqlbase.init_pool().")

        try:
            async with self.pool.acquire() as connection:
                async with connection.transaction():
                    if params:
                        return await connection.fetch(query, *params)
                    return await connection.fetch(query)
        except asyncpg.PostgresError as e:
            print(f"Ошибка выполнения запроса: {e}")
            raise
