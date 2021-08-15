from App.settings import DB_CONNECTION_STRING, DEBUG
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

__all__ = (
    'db_async_engine',
    'db_async_session',
    'db_session_getter',
    'db_model_base',

    'AsyncSession',
)


db_async_engine = create_async_engine(DB_CONNECTION_STRING, echo=DEBUG)
db_model_base = declarative_base()
db_async_session = sessionmaker(
    db_async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def db_session_getter() -> AsyncSession:
    async with db_async_session() as session:
        yield session
