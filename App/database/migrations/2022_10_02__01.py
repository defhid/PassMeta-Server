from App.database.migrations.base import BaseMigration


class Migration(BaseMigration):
    def __init__(self):
        super().__init__('2022.10.02 01')

    async def apply(self):
        await self.db.execute("""
            CREATE TABLE public.auth_keys (
                id serial PRIMARY KEY,
                user_id int NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
                secret_key uuid NOT NULL
            );
            CREATE UNIQUE INDEX IF NOT EXISTS auth_keys_user_id_uix ON public.auth_keys(user_id);
        """)
