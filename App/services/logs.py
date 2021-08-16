from App.utils.db import AsyncDbSession
from App.models.extra import LogKind
from App.models.db import Log, LogMore
from App.special import *


class LogService:
    __slots__ = ('db', )

    def __init__(self, db_session: AsyncDbSession):
        self.db = db_session

    async def write_log(self, kind: LogKind, entity_id: int = None, more: str = None):
        """ Auto-commit.
        """
        if entity_id is None and kind.entity_model is not None:
            raise Bad(None, SERVER_ERR, MORE.text(f"Attempting to log without required entity_id!"))

        log = Log(kind_id=kind.id, entity_id=entity_id)
        self.db.add(log)

        if more:
            log_more = LogMore(log_id=log.id, info=more)
            self.db.add(log_more)

        await self.db.commit()
