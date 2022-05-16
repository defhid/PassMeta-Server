from App.services.base import DbServiceBase
from App.settings import HISTORY_KEEP_MONTHS
from App.special import *
from App.models.entities import RequestInfo
from App.models.dto import HistoryPageParamsDto
from App.models.factory import PageFactory
from App.models.orm import History
from App.translate import HISTORY_KINDS_TRANSLATE_PACK, Locale, reverse_translate_package
from App.utils.db import MakeSql
from App.utils.scheduler import SchedulerTask
import datetime

__all__ = (
    'HistoryService',
)


class HistoryService(DbServiceBase):
    __slots__ = ()

    HISTORY_KINDS_CACHE = reverse_translate_package(HISTORY_KINDS_TRANSLATE_PACK,
                                                    lambda kind, name: {'id': kind, 'name': name})

    @classmethod
    def get_history_kinds(cls, request: RequestInfo) -> List[dict]:
        kinds = cls.HISTORY_KINDS_CACHE.get(request.locale)
        return kinds if kinds is not None else cls.HISTORY_KINDS_CACHE.get(Locale.DEFAULT)

    async def get_page(self, page: HistoryPageParamsDto, request: RequestInfo) -> Dict:
        params = {
            'offset': page.offset,
            'limit': page.limit,
            'affected_user_id': request.user_id,
            'kinds_condition': MakeSql.empty()
        }

        if page.kind:
            try:
                params['kinds'] = tuple(int(k) for k in page.kind.split(','))
                params['kinds_condition'] = self._KINDS_CONDITION
            except ValueError:
                raise Bad('kind', VAL_ERR, MORE.allowed('<id:int>,...'))

        total = await self.db.query_scalar(int, self._SELECT_HISTORY_COUNT, params)
        histories = await self.db.query_list(History, self._SELECT_HISTORY, params)

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

        return PageFactory.create(
            [h.to_dict(request.locale) for h in histories],
            total,
            page.offset,
            page.limit
        )

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

    _SELECT_OLD_TABLES = MakeSql("""
        WITH history_more_tables AS (
            SELECT table_name,
                   split_part(table_name, '_', 3)::int as year,
                   split_part(table_name, '_', 4)::int as month
            FROM information_schema.tables
            WHERE table_schema = 'history' 
              AND table_name SIMILAR TO 'history_more_\d\d\d\d_\d\d'
        )
        SELECT 'history.' || table_name
        FROM history_more_tables
        WHERE year < @year
           OR (year = @year AND month < @month)
    """)

    # endregion
