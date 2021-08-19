from App.utils.db import db_async_session
from App.models.db import Session
from App.settings import SESSION_LIFETIME_DAYS

from sqlalchemy import delete
from datetime import datetime, timedelta
import asyncio


class SessionUtils:
    @classmethod
    def check_old_sessions(cls):
        asyncio.run(cls._check_old_sessions())

    @classmethod
    async def _check_old_sessions(cls):
        expired = datetime.now() - timedelta(days=SESSION_LIFETIME_DAYS)
        async with db_async_session() as db:
            await db.execute(delete(Session).where(Session.created_on < expired))
