import logging

from faker import Faker

from environment import env_var, read_env

read_env()

LOG_LEVEL = env_var("LOG_LEVEL", "DEBUG").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s'
)
logging.getLogger("faker").setLevel(logging.WARNING)

fake = Faker("en_GB")

TSV_BASE_DIR = env_var("TSV_BASE_DIR", "tsv")

LOCAL_SECRETS = env_var("LOCAL_SECRETS", "False")
LOCAL_SECRETS_PATH = env_var("LOCAL_SECRETS_PATH", "local_secrets.json")

CHANNEL_VAULT_PATH = env_var("CHANNEL_VAULT_PATH", "/channels")
VAULT_URL = env_var("VAULT_URL")
VAULT_TOKEN = env_var("VAULT_TOKEN")

DB_USER = env_var("DB_USER", "postgres")
DB_PASSWORD = env_var("DB_PASSWORD", "")
DB_HOST = env_var("DB_HOST", "127.0.0.1")
DB_PORT = env_var("DB_PORT", "5432")
HERMES_DB = env_var("HERMES_DB", "hermes")
HADES_DB = env_var("HADES_DB", "hades")

HISTORY_DB_USER = env_var("DB_USER", "postgres")
HISTORY_DB_PASSWORD = env_var("DB_PASSWORD", "")
HISTORY_DB_HOST = env_var("DB_HOST", "127.0.0.1")
HISTORY_DB_PORT = env_var("DB_PORT", "5432")
HISTORY_DB = env_var("HERMES_DB", "hermeshistory")

HERMES_URL = env_var("HERMES_URL")
SERVICE_API_KEY = "F616CE5C88744DD52DB628FAD8B3D"
