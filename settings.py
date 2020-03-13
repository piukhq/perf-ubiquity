from faker import Faker

from environment import env_var, read_env

read_env()
fake = Faker("en_GB")

LOCAL_SECRETS = env_var("LOCAL_SECRETS", "False")
LOCAL_SECRETS_PATH = env_var("LOCAL_SECRETS_PATH", "local_secrets.json")

CHANNEL_VAULT_PATH = env_var("CHANNEL_VAULT_PATH")
VAULT_URL = env_var("VAULT_URL")
VAULT_TOKEN = env_var("VAULT_TOKEN")

DB_USER = env_var("DB_USER", "postgres")
DB_PASSWORD = env_var("DB_PASSWORD", "")
DB_HOST = env_var("DB_HOST", "127.0.0.1")
DB_PORT = env_var("DB_PORT", "5432")
HERMES_DB = env_var("HERMES_DB", "hermes")
HADES_DB = env_var("HADES_DB", "hades")
