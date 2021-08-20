from App.utils.scheduler import SchedulerTask
from App.models.db import Session
from App.settings import SESSION_LIFETIME_DAYS

from sqlalchemy import delete
from datetime import datetime, timedelta


class SessionUtils:
    @classmethod
    async def check_old_sessions(cls, context: 'SchedulerTask.Context'):
        expired = datetime.now() - timedelta(days=SESSION_LIFETIME_DAYS)
        async with context.db_utils.make_session() as db:
            await db.execute(delete(Session).where(Session.created_on < expired))
            await db.commit()
