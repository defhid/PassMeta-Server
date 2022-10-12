from App.models.entities import RequestInfo
from App.utils.history import HistoryWriter
from passql import DbConnection


class DbServiceBase:
    __slots__ = ('db', 'request', '_history_writer')

    def __init__(self, db_connection: DbConnection, request: RequestInfo):
        self.db = db_connection
        self.request = request

    @property
    def history_writer(self) -> HistoryWriter:
        if not hasattr(self, '_history_writer'):
            self._history_writer = HistoryWriter(self.db, self.request)
        return self._history_writer
