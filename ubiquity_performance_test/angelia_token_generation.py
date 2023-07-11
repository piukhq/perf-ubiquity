import json
import random
from datetime import UTC, datetime, timedelta

import jwt
from locust.env import Environment
from loguru import logger

from ubiquity_performance_test.data_population.fixtures.client import NON_RESTRICTED_CLIENTS, TRUSTED_CHANNEL_CLIENTS
from ubiquity_performance_test.request_data import angelia
from ubiquity_performance_test.settings import redis
from ubiquity_performance_test.vault import vault_secrets

channels_to_test = 0  # number of channels to be tested. Value assigned by locustfile
trusted_channels_to_test = 0  # number of trusted channels to be tested. Value assigned by locustfile


class TokenGen:
    def generate_tokens(self, environment: Environment) -> None:
        logger.info("Generating b2b_tokens")

        if not environment.runner:
            raise ValueError("Runner unexpectedly None")

        total_users = environment.runner.target_user_count
        redis.delete("user_tokens")  # Clear the list first to avoid expired tokens from previous tests

        for _ in range(total_users):
            user_tokens = self.generate_all_b2b_tokens()
            redis.lpush("user_tokens", json.dumps(user_tokens))

        logger.info(f"{total_users} tokens successfully pushed to Redis queue 'b2b_tokens'.")

    @staticmethod
    def setup_user_info() -> dict:
        data: dict = {}
        for user in ("primary_user", "secondary_user"):
            email, external_id = angelia.generate_random_email_and_sub()
            data[user] = {}
            data[user]["email"] = email
            data[user]["external_id"] = external_id
        return data

    @staticmethod
    def generate_b2b_token(email: str, sub: str, client_name: str, private_key: str) -> str:
        access_life_time = 86400
        iat = datetime.now(tz=UTC)
        exp = iat + timedelta(seconds=access_life_time)

        payload = {
            "email": email,
            "sub": sub,
            "iat": iat,
            "exp": exp,
        }
        headers = {"kid": f"{client_name}-2021-12-16"}
        # KIDs have trailing datetime to mimic real KID use cases. We don't need to cycle these so this date can be
        # hardcoded.

        return jwt.encode(payload=payload, key=private_key, algorithm="RS512", headers=headers)

    def generate_all_b2b_tokens(self) -> dict:
        private_key = vault_secrets.channel_info["api2_private_keys"]

        client_name = random.choice(NON_RESTRICTED_CLIENTS[:channels_to_test])["client_name"].replace(" ", "")
        trusted_channel_client_name = random.choice(TRUSTED_CHANNEL_CLIENTS[:trusted_channels_to_test])[
            "client_name"
        ].replace(" ", "")

        b2b_tokens = {}
        user_details = self.setup_user_info()

        for user in ("primary_user", "secondary_user"):
            email = user_details[user]["email"]
            sub = user_details[user]["external_id"]
            b2b_tokens[user] = self.generate_b2b_token(email, sub, client_name, private_key)

        for user in ("primary_user", "secondary_user"):
            email = user_details[user]["email"]
            sub = user_details[user]["external_id"]
            token = self.generate_b2b_token(email, sub, trusted_channel_client_name, private_key)
            b2b_tokens[f"trusted_channel_{user}"] = token

        logger.info(f"Generated test tokens: {b2b_tokens}")
        return b2b_tokens


def set_channels(channels: int, trusted_channels: int) -> None:
    global channels_to_test, trusted_channels_to_test  # noqa: PLW0603

    if channels < 1:
        raise ValueError("TOTAL_CHANNELS cannot be 0")
    if trusted_channels < 1:
        raise ValueError("TOTAL_TRUSTED_CHANNELS cannot be 0")
    if channels > len(NON_RESTRICTED_CLIENTS):
        raise ValueError("TOTAL_CHANNELS cannot be greater than number of client fixtures")
    if trusted_channels > len(TRUSTED_CHANNEL_CLIENTS):
        raise ValueError("TOTAL_TRUSTED_CHANNELS cannot be greater than number of trusted channel client fixtures")

    channels_to_test = channels
    trusted_channels_to_test = trusted_channels


tokens = TokenGen()
