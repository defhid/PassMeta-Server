from App.utils.db import AsyncDbSession
from App.models.extra import HistoryKind
from App.models.db import History, HistoryMore, User

from starlette.requests import Request
from typing import Optional

__all__ = (
    'HistoryWriter',
)


class HistoryWriter:
    __slots__ = ('db', )

    def __init__(self, db_session: AsyncDbSession):
        self.db = db_session

    async def write(self, kind: HistoryKind, user: Optional[User], more: str = None, request: Request = None):
        """ Auto-commit.
        """
        h = History(kind_id=kind.id, user_id=None if user is None else user.id)
        self.db.add(h)

        if request is not None:
            if more:
                more += f",host:{request.client.host},port:{request.client.port}"
            else:
                more = f"host:{request.client.host},port:{request.client.port}"

        if more:
            h_more = HistoryMore(history_id=h.id, info=more)
            self.db.add(h_more)

        await self.db.commit()
