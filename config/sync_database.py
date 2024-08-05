from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .environments import env


class SettingsDB:
    def __init__(self, env):
        self.env = env
        self.sync_engin = create_engine(url=self.database_url_sync, echo=False)
        self.sync_session = sessionmaker(self.sync_engin, autoflush=False, expire_on_commit=False)

    @property
    def database_url_sync(self):
        return f"postgresql+psycopg2://{self.env.DB_USER}:{self.env.DB_PASS}@{self.env.DB_HOST}:{self.env.DB_PORT}/{self.env.DB_NAME}"


db = SettingsDB(env)
