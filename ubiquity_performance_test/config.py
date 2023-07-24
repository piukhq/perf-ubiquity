import logging
from typing import Annotated, Literal

from bink_logging_utils import init_loguru_root_sink
from bink_logging_utils.handlers import loguru_intercept_handler_factory
from faker import Faker
from pydantic import Extra, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings
from redis import Redis


class Settings(BaseSettings):
    LOG_LEVEL: Literal["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG"
    JSON_LOGGING: bool = False

    TSV_BASE_DIR: str = "tsv"

    LOCAL_SECRETS: bool = False
    LOCAL_SECRETS_PATH: str = "local_secrets.json"

    REDIS_URL: Annotated[str, RedisDsn] = "redis://localhost:6379/0"
    REDIS_SPAWN_COMPLETED_KEY: str = "performance:ubiquity:spawning-complete"

    VAULT_URL: str
    AES_KEYS_VAULT_NAME: str = "aes-keys"
    API2_PRIVATE_KEYS_NAME: str = "api2-channel-private-keys"

    DB_CONNECTION_URI: Annotated[str, PostgresDsn]
    HERMES_DB: str = "hermes"
    HADES_DB: str = "hades"

    HERMES_URL: str
    SERVICE_API_KEY: str = "F616CE5C88744DD52DB628FAD8B3D"
    SECRETS_LOCATION: str | None = None

    class Config:
        extra = Extra.ignore
        case_sensitive = True
        # env var settings priority ie priority 1 will override priority 2:
        # 1 - env vars already loaded (ie the one passed in by kubernetes)
        # 2 - env vars read from *local.env file
        # 3 - values assigned directly in the Settings class
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()  # type: ignore [call-arg]


# setup logging
InterceptHandler = loguru_intercept_handler_factory()
init_loguru_root_sink(json_logging=settings.JSON_LOGGING, sink_log_level=settings.LOG_LEVEL, show_pid=False)
logging.basicConfig(handlers=[InterceptHandler()])
logging.getLogger("faker").setLevel(logging.WARNING)

fake = Faker("en_GB")
redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
