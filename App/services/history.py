from App.services.base import DbServiceBase
from App.settings import HISTORY_KEEP_MONTHS
from App.special import *
from App.models.entities import RequestInfo, PageRequest, PageResult
from App.models.db import History
from App.utils.db import MakeSql
from App.utils.scheduler import SchedulerTask
import datetime

__all__ = (
    'HistoryService',
)


class HistoryService(DbServiceBase):
    __slots__ = ()

    async def get_page(self, page: PageRequest, kind: str, request: RequestInfo) -> PageResult:
        if kind != 'all':
            kinds = kind.split(',')
            try:
                kinds = tuple(int(k) for k in kinds)
            except ValueError:
                raise Bad('kind', VAL_ERR, MORE.allowed('all', '<id:int>,'))
            else:
                page.kinds = kinds
                page.kinds_condition = self._KINDS_CONDITION
        else:
            page.kinds_condition = MakeSql.empty()

        page.affected_user_id = request.user_id

        total = await self.db.query_scalar(int, self._SELECT_HISTORY_COUNT, page)
        histories = await self.db.query_list(History, self._SELECT_HISTORY, page)

        timestamps = set(f"{h.timestamp.year}_{h.timestamp.month:02}" for h in histories)

        more_tables = await self.db.query_values_list(str, self._SELECT_MORE_TABLES, {
            'table_names': (("history_more_" + t) for t in timestamps)
        })

        history_ids = ','.join(str(h.id) for h in histories)
        sql = " UNION ALL ".join(f"SELECT history_id, info FROM history.{t} WHERE history_id IN ({history_ids})"
                                 for t in more_tables)

        mores = await self.db.query_values_dict('history_id', int, Tuple[int, str], sql)
        for history in histories:
            history.more = mores.get(history.id, (None, None))[1]

        return PageResult([h.to_dict(request.loc) for h in histories], total, page.offset, page.limit)

    @classmethod
    async def scheduled__check_old_histories(cls, context: 'SchedulerTask.Context') -> str:
        expire = datetime.date.today() - datetime.timedelta(days=HISTORY_KEEP_MONTHS)

        async with context.db_utils.context_connection() as db:
            tables = await db.query_values_list(str, cls._SELECT_OLD_TABLES, {
                'year': expire.year,
                'month': expire.month
            })
            if tables:
                await db.execute(';'.join(f"DROP TABLE {t}" for t in tables))

        return ', '.join(tables)

    # region SQL

    _SELECT_HISTORY_COUNT = MakeSql("""
            SELECT count(*) FROM history.history h
            WHERE h.affected_user_id = @affected_user_id @kinds_condition
        """)

    _SELECT_HISTORY = MakeSql("""
        SELECT h.*, u.login as user_login, NULL as affected_user_login
        FROM history.history h
            LEFT JOIN "user" u ON u.id = h.user_id
        WHERE h.affected_user_id = @affected_user_id @kinds_condition
        ORDER BY h.id DESC
        OFFSET @offset LIMIT @limit
    """)

    _KINDS_CONDITION = MakeSql("""AND h.kind_id IN (@kinds)""")

    _SELECT_MORE_TABLES = MakeSql("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'history' AND table_name IN (@table_names)
    """)

    _SELECT_MORE = MakeSql("""""")

    _SELECT_OLD_TABLES = MakeSql("""
        WITH history_more_tables AS (
            SELECT table_name,
                   split_part(table_name, '_', 3)::int as year,
                   split_part(table_name, '_', 4)::int as month
            FROM information_schema.tables
            WHERE table_schema = 'history' 
              AND table_name SIMILAR TO 'history_more_\d\d\d\d_\d\d'
        )
        SELECT table_name
        FROM history_more_tables
        WHERE year < @year
           OR (year = @year AND month < @month)
    """)

    # endregion
