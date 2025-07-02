from enum import Enum
from functools import lru_cache
from typing import List
from pydantic import validator
from pydantic_settings import BaseSettings


class Environment(str, Enum):
    LOCAL = "local"
    DEV = "dev"
    PROD = "prod"


class DatabaseSettings(BaseSettings):
    user: str = "postgres"
    password: str = "postgres"
    host: str = "localhost"
    port: int = 5432
    database: str = "open_launch"

    class Config:
        env_prefix = "POSTGRES_"
        env_file = ".env"
        extra = "ignore"

    @property
    def sync_url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    @property
    def async_url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class RabbitMQSettings(BaseSettings):
    user: str = "guest"
    password: str = "guest"
    host: str = "localhost"
    port: int = 5672

    class Config:
        env_prefix = "RABBITMQ_"
        env_file = ".env"
        extra = "ignore"

    @property
    def url(self) -> str:
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}//"


class Settings(BaseSettings):
    environment: Environment = Environment.LOCAL
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "info"
    app_reload: bool = False

    database: DatabaseSettings = DatabaseSettings()
    rabbitmq: RabbitMQSettings = RabbitMQSettings()

    secret_key: str = "supersecretkey"
    access_token_expire_minutes: int = 30

    allowed_origins: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://127.0.0.1",
    ]

    @validator("log_level")
    def validate_log_level(cls, v):
        valid_levels = ["critical", "error", "warning", "info", "debug", "trace"]
        if v.lower() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v.lower()

    @property
    def is_production(self) -> bool:
        return self.environment == Environment.PROD


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


@lru_cache()
def get_database_settings() -> DatabaseSettings:
    return DatabaseSettings()
