from App.utils.db import AsyncDbSession
from App.utils.history import HistoryWriter


class DbServiceBase:
    __slots__ = ('db', '_history_writer')

    def __init__(self, db_session: AsyncDbSession):
        self.db = db_session

    @property
    def history_writer(self) -> HistoryWriter:
        if not hasattr(self, '_history_writer'):
            self._history_writer = HistoryWriter(self.db)
        return self._history_writer
