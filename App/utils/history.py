from App.database import MakeSql, History
from App.models.entities import RequestInfo
from App.utils.logging import LoggerFactory
from App.special import *

from passql import DbConnection
from typing import Optional
import ipaddress

__all__ = (
    'HistoryWriter',
)


class HistoryWriter:
    __slots__ = ('db', 'request')

    logger = LoggerFactory.get_named("HISTORY WRITER")

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

    def operation(self,
                  success_kind_id: int,
                  failure_kind_id: int,
                  affected_user_id: int = None,
                  affected_passfile_id: int = None) -> 'HistoryOperation':
        operation = HistoryOperation(self, success_kind_id, failure_kind_id)
        operation.affected_user_id = affected_user_id
        operation.affected_passfile_id = affected_passfile_id
        return operation

    # region SQL

    _ADD_HISTORY = MakeSql("""
        SELECT history.add_history(
        #kind_id::smallint, #user_ip::bigint, #user_id::bigint, 
        #affected_user_id::bigint, #affected_passfile_id::bigint, #more::char(10))
    """)

    # endregion


class HistoryOperation:
    __slots__ = (
        '_executed',
        '_history_writer',
        '_success_kind_id',
        '_failure_kind_id',
        'affected_user_id',
        'affected_passfile_id',
        'transaction',
    )

    logger = LoggerFactory.get_named("HISTORY OPERATION")

    def __init__(self, history_writer: 'HistoryWriter', success_kind_id: int, failure_kind_id: int):
        self._history_writer = history_writer
        self._success_kind_id = success_kind_id
        self._failure_kind_id = failure_kind_id
        self._executed = False

    async def __aenter__(self) -> 'HistoryOperation':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._executed:
            return

        if exc_val is None:
            if self.transaction is None:
                self.logger.critical("Transaction is not started before writing scoped history!")
                await self.start_db_transaction()
            try:
                await self._history_writer.write(
                    self._success_kind_id,
                    self.affected_user_id,
                    self.affected_passfile_id,
                    None
                )
                await self.transaction.commit()
            except Exception:
                await self.transaction.rollback()
                raise
        else:
            if self.transaction is not None:
                await self.transaction.rollback()
            await self._history_writer.write(
                self._failure_kind_id,
                self.affected_user_id,
                self.affected_passfile_id,
                get_more_from_bad(exc_val) if isinstance(exc_val, Bad)
                else "EXCEPTION" if exc_val is not None
                else None
            )

        self._executed = True

    def with_affected_passfile(self, passfile_id: Optional[int]) -> 'HistoryOperation':
        self.affected_passfile_id = passfile_id
        return self

    def with_affected_user(self, user_id: Optional[int]) -> 'HistoryOperation':
        self.affected_user_id = user_id
        return self

    async def start_db_transaction(self):
        self.transaction = self._history_writer.db.transaction()
        await self.transaction.start()

    async def raise_bad(self, bad: Bad, history_more: str = None):
        if self.transaction is not None:
            await self.transaction.rollback()

        await self._history_writer.write(
            self._failure_kind_id,
            self.affected_user_id,
            self.affected_passfile_id,
            history_more if history_more is not None else get_more_from_bad(bad)
        )

        self._executed = True
        raise bad


def get_more_from_bad(bad: Bad):
    if bad.code is ACCESS_ERR:
        return "ACCESS"
    if bad.code is NOT_EXIST_ERR:
        return "NOT EXIST"
    if bad.code is SERVER_ERR:
        return "SERVER ERR"
    return "BAD" + str(bad.code.code)
