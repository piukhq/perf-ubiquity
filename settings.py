from faker import Faker

from environment import env_var, read_env

read_env()
fake = Faker("en_GB")

LOCAL_SECRETS = env_var("LOCAL_SECRETS", "False")
LOCAL_SECRETS_PATH = env_var("LOCAL_SECRETS_PATH", "local_secrets.json")

CHANNEL_VAULT_PATH = env_var("CHANNEL_VAULT_PATH")
VAULT_URL = env_var("VAULT_URL")
VAULT_TOKEN = env_var("VAULT_TOKEN")
