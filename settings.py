from faker import Faker

from environment import env_var, read_env

read_env()
fake = Faker("en_GB")

TSV_PATH = "tsv"

CHANNEL_VAULT_PATH = env_var("CHANNEL_VAULT_PATH")
VAULT_URL = env_var("VAULT_URL")
VAULT_TOKEN = env_var("VAULT_TOKEN")
