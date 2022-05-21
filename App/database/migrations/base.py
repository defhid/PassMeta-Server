from datetime import datetime
from typing import Optional
from passql import DbConnection
import re


class BaseMigration:
    NAME_PATTERN = re.compile(r'^\d\d\d\d.\d\d.\d\d \d\d+$')  # date & number in scope of this date

    __slots__ = ('date', 'ordering', 'name', 'db')

    def __init__(self, name: str):
        name = name.strip()
        assert re.fullmatch(self.NAME_PATTERN, name), "Incorrect migration format"

        parts = name.split(' ')

        self.date = datetime(*map(int, parts[0].split('.')))
        self.ordering = int(parts[1])
        self.name = (str(self.date.year) +
                     str(self.date.month).rjust(2, '0') +
                     str(self.date.day).rjust(2, '0') +
                     str(self.ordering).rjust(4, '0'))

        self.db: Optional[DbConnection] = None

    async def apply(self):
        ...

    async def execute(self, db: DbConnection):
        self.db = db
        async with db.transaction():
            await self.apply()
            await db.execute("INSERT INTO migrations (name) VALUES (@name)", self)
        self.db = None
