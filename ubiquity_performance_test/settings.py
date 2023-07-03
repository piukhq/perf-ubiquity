import logging

from bink_logging_utils import init_loguru_root_sink
from bink_logging_utils.factories import loguru_intercept_handler_factory
from decouple import Choices, config
from faker import Faker

InterceptHandler = loguru_intercept_handler_factory()


LOG_LEVEL = config("LOG_LEVEL", "DEBUG", cast=Choices(("NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")))
JSON_LOGGING: bool = config("JSON_LOGGING", False, cast=bool)

init_loguru_root_sink(json_logging=JSON_LOGGING, sink_log_level=LOG_LEVEL, show_pid=False)
logging.basicConfig(handlers=[InterceptHandler()])
logging.getLogger("faker").setLevel(logging.WARNING)

fake = Faker("en_GB")

TSV_BASE_DIR: str = config("TSV_BASE_DIR", "tsv")

LOCAL_SECRETS: bool = config("LOCAL_SECRETS", False, cast=bool)
LOCAL_SECRETS_PATH: str = config("LOCAL_SECRETS_PATH", "local_secrets.json")

REDIS_URL: str = config("REDIS_URL", "redis://localhost:6379/0")

VAULT_CONFIG: dict[str, str] = {
    "VAULT_URL": config("VAULT_URL", ""),
    "AES_KEYS_VAULT_NAME": config("AES_KEYS_VAULT_NAME", "aes-keys"),
    "API2_PRIVATE_KEYS_NAME": config("API2_PRIVATE_KEYS_NAME", "api2-channel-private-keys"),
}

DB_CONNECTION_URI: str = config("DB_CONNECTION_URI")
HERMES_DB: str = config("HERMES_DB", "hermes")
HADES_DB: str = config("HADES_DB", "hades")

HERMES_URL: str = config("HERMES_URL")
SERVICE_API_KEY = "F616CE5C88744DD52DB628FAD8B3D"
SECRETS_LOCATION: str | None = config("SECRETS_LOCATION", None)
