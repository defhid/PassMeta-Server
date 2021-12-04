from App.services.base import DbServiceBase
from App.settings import HISTORY_KEEP_MONTHS
from App.special import *
from App.models.request import HistoryPage
from App.models.db import User, History
from App.utils.db import MakeSql
from App.utils.scheduler import SchedulerTask
import datetime

__all__ = (
    'HistoryService',
)


class HistoryService(DbServiceBase):
    __slots__ = ()

    async def get_page(self, params: HistoryPage, user: User) -> Tuple[int, List[History]]:
        pass  # TODO

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

    _SELECT_OLD_TABLES = MakeSql("""
        WITH history_more_tables AS (
            SELECT table_name,
                   split_part(table_name, '_', 3)::int as year,
                   split_part(table_name, '_', 4)::int as month
            FROM information_schema.tables
            WHERE table_schema = 'public' 
              AND table_name SIMILAR TO 'history_more_\d\d\d\d_\d\d'
        )
        SELECT table_name
        FROM history_more_tables
        WHERE year < @year
           OR (year = @year AND month < @month)
    """)

    # endregion
