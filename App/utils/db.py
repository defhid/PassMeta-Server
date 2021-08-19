from App.settings import DB_CONNECTION_STRING, DB_CONNECTION_POOL_SIZE, DEBUG

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.sql.expression import Select
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool

from typing import Optional, Iterable, TypeVar, Type, Generator

__all__ = (
    'AsyncDbSession',
    'DbModelBase',
    'DbUtils',
)


MT = TypeVar('MT', bound='DbModelBase')  # model type


class AsyncDbSession(AsyncSession):
    @classmethod
    def _regenerate_proxy_for_target(cls, target):
        return super()._regenerate_proxy_for_target(target)

    async def query_first(self, _: Type[MT], query: Select) -> Optional[MT]:
        return (await self.execute(query.limit(1))).scalar()

    async def query(self, _: Type[MT], query: Select) -> Iterable[MT]:
        return map(lambda row: row[0], await self.execute(query))


db_async_engine = create_async_engine(
    DB_CONNECTION_STRING,
    pool_size=DB_CONNECTION_POOL_SIZE,
    max_overflow=0,
    poolclass=QueuePool,
    echo=DEBUG
)

DbModelBase = declarative_base()

db_async_session = sessionmaker(
    db_async_engine,
    class_=AsyncDbSession,
    expire_on_commit=False,
)


class DbUtils:
    @staticmethod
    async def session_maker() -> Generator[AsyncDbSession, None, None]:
        """ Yields session in 'with' scope.
        """
        async with db_async_session() as session:
            yield session

    @staticmethod
    async def ensure_models_created():
        """ Create non-existent DB tables (models).
        """
        async with db_async_engine.begin() as conn:
            await conn.run_sync(DbModelBase.metadata.create_all)

    @staticmethod
    def make_session() -> AsyncDbSession:
        return db_async_session()
