from pathlib import Path
from typing import Literal

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR: Path = Path(__file__).parent.parent


class DBConfig(BaseModel):
    ### sqlalchemy
    DB_ECHO: bool = False
    DB_EXPIRE_ON_COMMIT: bool = False
    DB_AUTOFLUSH: bool = False
    DB_AUTOCOMMIT: bool = False
    NAMING_CONVENTION: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    ### database config
    DB_HOST: str
    DB_USER: str
    DB_NAME: str
    DB_PORT: int
    DB_PASSWORD: str
    DB_NAME_TEST: str = "postgres"

    @property
    def DB_URL(self) -> str:
        url: str = f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return url


class GunicornConfig(BaseModel):
    GUNICORN_PORT: int = 8888
    GUNICORN_RELOAD: bool = False
    GUNICORN_HOST: str = "0.0.0.0"
    GUNICORN_WORKERS: int = 1
    GUNICORN_TIMEOUT: int = 900
    GUNICORN_WORKERS_CLASS: str = "uvicorn.workers.UvicornWorker"
    GUNICORN_ERROR_LOG: str | None = "-"
    GUNICORN_ACCESS_LOG: str | None = "-"


class UvicornConfig(BaseModel):
    UVICORN_PORT: int = 8888
    UVICORN_HOST: str = "127.0.0.1"
    UVICORN_RELOAD: bool = True


class GeneralAppConfig(BaseModel):
    TITLE: str = "FastAPI Quick Start"
    MODE: Literal["TEST", "DEV"]


class Settings(BaseSettings):
    db: DBConfig
    app: GeneralAppConfig
    gunicorn: GunicornConfig = GunicornConfig()
    uvicorn: UvicornConfig = UvicornConfig()

    model_config = SettingsConfigDict(
        env_file=(BASE_DIR / ".env",),
        extra="ignore",
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="CFG_",
    )


settings = Settings()  # type: ignore
