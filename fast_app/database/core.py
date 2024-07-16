from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config.environments import env
#url = f"postgresql+asyncpg://Alexandr:asusk52j@localhost:5432/postgres"
engine = create_async_engine(url=env.database_url_async, echo=True)
session = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)


async def close_session():
    async with session() as sos:
        await sos.close()
