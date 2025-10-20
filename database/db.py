from typing import Union, Tuple, List, Optional
import asyncpg

from config import HOST_POSTGRES, PASSWORD_POSTGRES, DATABASE_POSTGRES, USER_POSTGRES

pg_host = HOST_POSTGRES
pg_user = USER_POSTGRES
pg_password = PASSWORD_POSTGRES
pg_database = DATABASE_POSTGRES

_pool: asyncpg.Pool | None = None


class Sqlbase:

    def __init__(self, pool=None):
        self.pool = pool or _pool
        print(pg_user)

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

    async def execute_transaction(
            self,
            queries: List[Tuple[str, Optional[tuple]]]
    ) -> List[Union[list, None]]:
        """
        Выполняет несколько SQL-запросов в рамках одной транзакции.
        :param queries: список кортежей (sql, params)
        :return: список результатов выполнения запросов
        """
        if not self.pool:
            raise ValueError("Пул соединений не создан. Убедитесь, что вызвали connect().")

        results = []
        try:
            async with self.pool.acquire() as connection:
                async with connection.transaction():
                    for query, params in queries:
                        if params:
                            result = await connection.fetch(query, *params)
                        else:
                            result = await connection.fetch(query)
                        results.append(result)
            return results

        except asyncpg.PostgresError as e:
            print(f"Ошибка выполнения транзакции: {e}")
            raise
