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
ST = TypeVar('ST')  # scalar type


class AsyncDbSession(AsyncSession):
    @classmethod
    def _regenerate_proxy_for_target(cls, target):
        return super()._regenerate_proxy_for_target(target)

    async def query_first(self, _: Type[MT], query: Select) -> Optional[MT]:
        return (await self.execute(query.limit(1))).scalar()

    async def query_scalar(self, _: Type[ST], query: Select) -> Optional[ST]:
        return (await self.execute(query.limit(1))).scalar()

    async def query(self, _: Type[MT], query: Select) -> Iterable[MT]:
        return map(lambda row: row[0], await self.execute(query))


class DbUtils:
    __slots__ = ('async_engine', '_async_session_maker')

    def __init__(self):
        self.async_engine = create_async_engine(
            DB_CONNECTION_STRING,
            pool_size=DB_CONNECTION_POOL_SIZE,
            max_overflow=0,
            poolclass=QueuePool,
            echo=DEBUG
        )
        self._async_session_maker = sessionmaker(
            self.async_engine,
            class_=AsyncDbSession,
            expire_on_commit=False,
        )

    async def session_maker(self) -> Generator[AsyncDbSession, None, None]:
        """ Yields session in 'with' scope.
        """
        async with self._async_session_maker() as session:
            yield session

    async def ensure_models_created(self):
        """ Create non-existent DB tables (models).
        """
        async with self.async_engine.begin() as conn:
            await conn.run_sync(DbModelBase.metadata.create_all)

    def make_session(self) -> AsyncDbSession:
        return self._async_session_maker()


DbModelBase = declarative_base()
