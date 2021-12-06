from App.settings import DB_CONNECTION, DB_CONNECTION_POOL_MIN_SIZE
from passql.defaults import SqlDefaultConverters
from passql import *
from typing import Generator
from types import GeneratorType
import asyncpg

__all__ = (
    'DbUtils',
    'MakeSql',
)


def _custom_sql_in(val, converter) -> str:
    result = ','.join(converter(v) for v in val)
    return result if result else 'SELECT NULL WHERE FALSE'


MakeSql = SqlMaker(SqlDefaultConverters.POSTGRES + SqlConverter({
    tuple: _custom_sql_in,
    range: _custom_sql_in,
    GeneratorType: _custom_sql_in,
}))


class DbUtils:
    __slots__ = ('_pool_size', '_connection_pool')

    def __init__(self, pool_size: int):
        self._pool_size = pool_size

    async def init(self) -> 'DbUtils':
        """ Initializes connection pool and returns self.
        """
        self._connection_pool = await asyncpg.create_pool(
            **DB_CONNECTION,
            min_size=min(self._pool_size, DB_CONNECTION_POOL_MIN_SIZE),
            max_size=self._pool_size
        )
        return self

    async def dispose(self):
        """ Closes the connection pool.
        """
        await self._connection_pool.close()

    async def connection_maker(self) -> Generator[DbConnection, None, None]:
        """ Resolves a connection and yields it.
        """
        origin_connection = await self._connection_pool.acquire()
        try:
            yield DbConnection(origin_connection, MakeSql)
        finally:
            await self._connection_pool.release(origin_connection)

    async def resolve_connection(self) -> DbConnection:
        """ Acquires a connection from the pool.
        """
        return DbConnection(await self._connection_pool.acquire(), MakeSql)

    async def release_connection(self, connection: DbConnection):
        """ Returns the connection back to the pool.
        """
        await self._connection_pool.release(connection.origin_connection)

    def context_connection(self) -> 'ContextConnectionResolver':
        """ Returns connection resolver for 'async with' construction.
        """
        return ContextConnectionResolver(self)


class ContextConnectionResolver:
    __slots__ = ('_db_utils', '_conn')

    def __init__(self, db_utils: 'DbUtils'):
        self._db_utils = db_utils

    async def __aenter__(self) -> 'DbConnection':
        self._conn = await self._db_utils.resolve_connection()
        return self._conn

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._db_utils.release_connection(self._conn)
        self._conn = None
