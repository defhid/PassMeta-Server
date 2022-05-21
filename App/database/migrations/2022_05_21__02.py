from App.database.migrations.base import BaseMigration


class Migration(BaseMigration):
    def __init__(self):
        super().__init__('2022.05.21 02')

    async def apply(self):
        await self.db.execute("""
            ALTER TABLE public.passfiles
            ADD COLUMN type_id smallint NOT NULL DEFAULT 1;

            ALTER TABLE public.passfiles ALTER COLUMN type_id DROP DEFAULT;
        """)
