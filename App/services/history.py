from App.models.dto.mapping import HistoryMapping
from App.models.dto.responses import HistoryPageDto, HistoryKindDto
from App.models.okbad import *
from App.services.base import DbServiceBase
from App.settings import HISTORY_KEEP_MONTHS
from App.models.entities import RequestInfo
from App.models.dto.requests import HistoryPageParamsDto
from App.database import MakeSql, History
from App.translate import HISTORY_KINDS_TRANSLATE_PACK, Locale, reverse_translate_package
from App.utils.scheduler import SchedulerTask
import datetime

__all__ = (
    'HistoryService',
)


class HistoryService(DbServiceBase):
    __slots__ = ()

    HISTORY_KINDS_CACHE = reverse_translate_package(HISTORY_KINDS_TRANSLATE_PACK,
                                                    lambda kind, name: HistoryKindDto.model_construct(id=kind, name=name))

    @classmethod
    def get_history_kinds(cls, request: RequestInfo) -> list[HistoryKindDto]:
        kinds = cls.HISTORY_KINDS_CACHE.get(request.locale)
        return kinds if kinds is not None else cls.HISTORY_KINDS_CACHE.get(Locale.DEFAULT)

    async def get_page(self, page: HistoryPageParamsDto) -> HistoryPageDto:
        params = {
            'history_table': MakeSql(f"histories_{page.month.year}_{page.month.month:02}"),
            'offset': page.page_size * page.page_index,
            'limit': page.page_size,
            'affected_user_id': self.request.user_id,
            'kinds_condition': MakeSql.empty()
        }

        if page.kind:
            try:
                params['kinds'] = [int(k) for k in page.kind.split(',')]
                params['kinds_condition'] = self._KINDS_CONDITION
            except ValueError:
                raise Bad(VALIDATION_ERR, MORE.format_wrong(WHAT.HISTORY.kind, '<id:int>,...'))

        exists = await self.db.query_scalar(bool, self._CHECK_TABLE_EXISTS, params)

        if exists:
            total = await self.db.query_scalar(int, self._SELECT_COUNT, params)
            histories = await self.db.query_list(History, self._SELECT_LIST, params)
        else:
            total = 0
            histories = []

        return HistoryPageDto.model_construct(
            list=[HistoryMapping.to_dto(h, self.request.locale) for h in histories],
            total=total,
            page_size=page.page_size,
            page_index=page.page_index
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

    _CHECK_TABLE_EXISTS = MakeSql("""
        SELECT EXISTS(
            SELECT FROM information_schema.tables
            WHERE table_schema = 'history' AND table_name = '#history_table')
    """)

    _SELECT_COUNT = MakeSql("""
        SELECT count(*) FROM history.#history_table h
        WHERE h.affected_user_id = #affected_user_id #kinds_condition
    """)

    _SELECT_LIST = MakeSql("""
        SELECT h.*, u.login as user_login, NULL as affected_user_login, pf.name as affected_passfile_name
        FROM history.#history_table h
            LEFT JOIN users u ON u.id = h.user_id
            LEFT JOIN passfiles pf ON pf.id = h.affected_passfile_id
        WHERE h.affected_user_id = #affected_user_id #kinds_condition
        ORDER BY h.id DESC
        OFFSET #offset LIMIT #limit
    """)

    _KINDS_CONDITION = MakeSql("""AND h.kind_id = any(#kinds)""")

    _SELECT_OLD_TABLES = MakeSql("""
        WITH history_tables AS (
            SELECT table_name,
                   split_part(table_name, '_', 3)::int as year,
                   split_part(table_name, '_', 4)::int as month
            FROM information_schema.tables
            WHERE table_schema = 'history' 
              AND table_name SIMILAR TO 'histories_\\d\\d\\d\\d_\\d\\d'
        )
        SELECT 'history.' || table_name
        FROM history_tables
        WHERE year < #year
           OR (year = #year AND month < #month)
    """)

    # endregion
