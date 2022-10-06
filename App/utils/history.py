from App.database import MakeSql, History

from passql import DbConnection
from typing import Optional

__all__ = (
    'HistoryWriter',
)


class HistoryWriter:
    __slots__ = ('db', )

    def __init__(self, db_connection: DbConnection):
        self.db = db_connection

    async def write(self,
                    kind_id: int,
                    user_id: Optional[int],
                    affected_user_id: Optional[int],
                    affected_passfile_id: Optional[int],
                    more: str = None) -> History:
        """ Write history.

        :param kind_id: History kind identifier.
        :param user_id: Actor user id.
        :param affected_user_id: Affected user id.
        :param affected_passfile_id: Affected passfile id.
        :param more: Additional text information.
        :return: Created history object.
        """

        h = History()
        h.kind_id = kind_id
        h.user_id = user_id
        h.affected_user_id = affected_user_id
        h.affected_passfile_id = affected_passfile_id
        h.more = more

        h.id = await self.db.query_scalar(int, self._ADD_HISTORY, h)
        return h

    # region SQL

    _ADD_HISTORY = MakeSql("""
        SELECT history.add_history(
        @kind_id::smallint, @user_id::bigint, 
        @affected_user_id::bigint, @affected_passfile_id::bigint, @more::char(10))
    """)

    # endregion
