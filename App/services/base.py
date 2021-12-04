from App.utils.history import HistoryWriter
from passql import DbConnection


class DbServiceBase:
    __slots__ = ('db', '_history_writer')

    def __init__(self, db_connection: DbConnection):
        self.db = db_connection

    @property
    def history_writer(self) -> HistoryWriter:
        if not hasattr(self, '_history_writer'):
            self._history_writer = HistoryWriter(self.db)
        return self._history_writer
