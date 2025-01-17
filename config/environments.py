from pydantic_settings import BaseSettings
from sqlalchemy.orm import declarative_base


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
    SECRET_KEY: str
    ALGORITHM: str

    class Config:
        env_file = ".env"


env = Settings()

Base = declarative_base()
