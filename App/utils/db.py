from App.settings import DB_CONNECTION_STRING, DEBUG
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql.expression import Select, Executable
from typing import Optional, Iterable, TypeVar, Type

__all__ = (
    'db_async_engine',
    'db_async_session',
    'db_session_getter',
    'db_model_base',

    'AsyncDbSession',
)


MT = TypeVar('MT', bound='db_model_base')  # model type
ST = TypeVar('ST')  # scalar type


class AsyncDbSession(AsyncSession):
    @classmethod
    def _regenerate_proxy_for_target(cls, target):
        return super()._regenerate_proxy_for_target(target)

    async def query_first(self, _: Type[MT], query: Select) -> Optional[MT]:
        return (await self.execute(query.limit(1))).scalar()

    async def query(self, _: Type[MT], query: Select) -> Iterable[MT]:
        return map(lambda row: row[0], await self.execute(query))


db_async_engine = create_async_engine(DB_CONNECTION_STRING, echo=DEBUG)
db_model_base = declarative_base()
db_async_session = sessionmaker(
    db_async_engine,
    class_=AsyncDbSession,
    expire_on_commit=False
)


async def db_session_getter() -> AsyncDbSession:
    async with db_async_session() as session:
        yield session
