from App.models.db import DbModelBase
from App.settings import DB_CONNECTION_STRING
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
import asyncio

__all__ = (
    'db_engine',
    'db_async_session',
    'db_session_getter',

    'AsyncSession',
)


db_engine = create_async_engine(DB_CONNECTION_STRING, echo=True)
db_async_session = sessionmaker(
    db_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def db_session_getter() -> AsyncSession:
    async with db_async_session() as session:
        yield session


async def _ensure_models_created():
    async with db_engine.begin() as conn:
        await conn.run_sync(DbModelBase.metadata.create_all)


asyncio.run(_ensure_models_created())
