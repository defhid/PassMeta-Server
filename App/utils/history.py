from App.models.db import History
from App.models.entities import RequestInfo

from passql import DbConnection
from typing import Optional

__all__ = (
    'HistoryWriter',
)

from App.utils.db import MakeSql


class HistoryWriter:
    __slots__ = ('db', )

    def __init__(self, db_connection: DbConnection):
        self.db = db_connection

    async def write(self,
                    kind_id: int,
                    user_id: Optional[int],
                    affected_user_id: Optional[int],
                    more: str = None,
                    request: RequestInfo = None) -> History:
        """ Write history.

        :param kind_id: History kind identifier.
        :param user_id: Actor user id.
        :param affected_user_id: Affected user id.
        :param more: Additional text information.
        :param request: Current request.
        :return: Created history object.
        """

        if request is not None:
            if more:
                more += f",host:{request.request.client.host}"
            else:
                more = f"host:{request.request.client.host}"

        h = History()
        h.kind_id = kind_id
        h.user_id = user_id
        h.affected_user_id = affected_user_id
        h.more = more

        h.id = await self.db.query_scalar(int, self._ADD_HISTORY_WITH_MORE if more else self._ADD_HISTORY, h)
        return h

    # region SQL

    _ADD_HISTORY = MakeSql("""
        INSERT INTO history.history (kind_id, user_id, affected_user_id)
        VALUES (@kind_id, @user_id, @affected_user_id)
        RETURNING *
    """)

    _ADD_HISTORY_WITH_MORE = MakeSql("""
        WITH his AS (
            INSERT INTO history.history (kind_id, user_id, affected_user_id)
            VALUES (@kind_id, @user_id, @affected_user_id)
            RETURNING *
        )
        SELECT add_history_more(id, @more) as history_id FROM his
    """)

    # endregion
