from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TOKEN: str
    PROJECT_NAME: str
    CORS_ALLOWED_ORIGINS: str
    MAIN_HOST: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    DB_PORT: int
    DB_HOST: str

    class Config:
        env_file = ".env"

    @property
    def database_url_async(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def database_url_sync(self):
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


env = Settings()
