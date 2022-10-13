from App.database import MakeSql, History
from App.models.entities import RequestInfo

from passql import DbConnection
from typing import Optional
import ipaddress

__all__ = (
    'HistoryWriter',
)


class HistoryWriter:
    __slots__ = ('db', 'request')

    def __init__(self, db_connection: DbConnection, request: RequestInfo):
        self.db = db_connection
        self.request = request

    async def write(self,
                    kind_id: int,
                    affected_user_id: Optional[int],
                    affected_passfile_id: Optional[int],
                    more: str = None,
                    user_id: int = None):
        h = History()
        h.kind_id = kind_id
        h.user_ip = int(ipaddress.ip_address(self.request.request.client.host))
        h.user_id = self.request.user_id if user_id is None else user_id
        h.affected_user_id = affected_user_id
        h.affected_passfile_id = affected_passfile_id
        h.more = more

        await self.db.execute(self._ADD_HISTORY, h)

    # region SQL

    _ADD_HISTORY = MakeSql("""
        SELECT history.add_history(
        #kind_id::smallint, #user_ip::bigint, #user_id::bigint, 
        #affected_user_id::bigint, #affected_passfile_id::bigint, #more::char(10))
    """)

    # endregion
