import logging

from faker import Faker

from environment import env_var, read_env

read_env()

LOG_LEVEL = env_var("LOG_LEVEL", "DEBUG").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s")
logging.getLogger("faker").setLevel(logging.WARNING)

fake = Faker("en_GB")

TSV_BASE_DIR = env_var("TSV_BASE_DIR", "tsv")

LOCAL_SECRETS = env_var("LOCAL_SECRETS", "False")
LOCAL_SECRETS_PATH = env_var("LOCAL_SECRETS_PATH", "local_secrets.json")

CHANNEL_SECRET_NAME = env_var("CHANNEL_SECRET_NAME", "channels")

VAULT_CONFIG = dict(
    VAULT_URL=env_var("VAULT_URL", ""),
    AES_KEYS_VAULT_NAME=env_var("AES_KEYS_VAULT_NAME", "aes-keys"),
    API2_ACCESS_SECRETS_NAME=env_var("API2_ACCESS_SECRETS_NAME", "api2-access-secrets"),
    API2_B2B_SECRETS_BASE_NAME=env_var("API2_B2B_SECRETS_BASE_NAME", "api2-b2b-secrets-"),
    API2_B2B_TOKEN_KEYS_BASE_NAME=env_var("API2_B2B_TOKEN_KEYS_BASE_NAME", "api2-b2b-token-key-")
)

DB_CONNECTION_URI = env_var("DB_CONNECTION_URI")
HERMES_DB = env_var("HERMES_DB", "hermes")
HADES_DB = env_var("HADES_DB", "hades")

HERMES_URL = env_var("HERMES_URL")
SERVICE_API_KEY = "F616CE5C88744DD52DB628FAD8B3D"
