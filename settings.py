from faker import Faker

from environment import env_var, read_env

read_env()
fake = Faker("en_GB")

TSV_PATH = "tsv"

JWT_SECRET = env_var("JWT_SECRET")
BARCLAYS_CLIENT_ID = env_var("BARCLAYS_CLIENT_ID")
