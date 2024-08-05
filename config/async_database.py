from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from .environments import env


class SettingsDB:
    def __init__(self, env):
        self.env = env
        self.engine = create_async_engine(url=self.database_url_async, echo=False)
        self.session = async_sessionmaker(self.engine, autoflush=False, expire_on_commit=False)

    @property
    def database_url_async(self):
        return f"postgresql+asyncpg://{self.env.DB_USER}:{self.env.DB_PASS}@{self.env.DB_HOST}:{self.env.DB_PORT}/{self.env.DB_NAME}"


db = SettingsDB(env)


async def close_session():
    async with db.session() as sos:
        await sos.close()
