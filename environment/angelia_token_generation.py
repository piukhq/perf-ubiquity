import datetime
import json
import logging
import random

import jwt
import redis
from locust.env import Environment

import settings
from data_population.fixtures.client import NON_RESTRICTED_CLIENTS
from request_data import angelia
from vault import load_secrets

logger = logging.getLogger(__name__)
r = redis.from_url(settings.REDIS_URL)

channels_to_test = 0  # number of channels to be tested. Value assigned by locustfile


class TokenGen:
    def generate_tokens(self, environment: Environment) -> None:
        logger.info("Generating b2b_tokens")

        total_users = environment.runner.target_user_count
        r.delete("user_tokens")  # Clear the list first to avoid expired tokens from previous tests

        for i in range(total_users):
            user_tokens = self.generate_b2b_tokens()
            r.lpush("user_tokens", json.dumps(user_tokens))

        logger.info(f"{total_users} tokens successfully pushed to Redis queue 'b2b_tokens'.")

    @staticmethod
    def setup_user_info() -> dict:
        data = {}
        for user in ["primary_user", "secondary_user"]:
            email, external_id = angelia.generate_random_email_and_sub()
            data[user] = {}
            data[user]["email"] = email
            data[user]["external_id"] = external_id
        return data

    def generate_b2b_tokens(self) -> dict:

        private_key = load_secrets()["api2_private_keys"]

        client_name = random.choice(NON_RESTRICTED_CLIENTS[:channels_to_test])["client_name"].replace(" ", "")

        b2b_tokens = {}
        user_details = self.setup_user_info()

        for user in ["primary_user", "secondary_user"]:

            access_life_time = 86400
            iat = datetime.datetime.utcnow()
            exp = iat + datetime.timedelta(seconds=access_life_time)

            payload = {
                "email": user_details[user]["email"],
                "sub": user_details[user]["external_id"],
                "iat": iat,
                "exp": exp,
            }
            headers = {"kid": f"{client_name}-2021-12-16"}
            # KIDs have trailing datetime to mimic real KID use cases. We don't need to cycle these so this date can be
            # hardcoded.

            b2b_token = jwt.encode(payload=payload, key=private_key, algorithm="RS512", headers=headers)

            b2b_tokens[user] = b2b_token

        return b2b_tokens


def set_channels(channels: int):
    global channels_to_test
    if channels < 1:
        raise ValueError("TOTAL_CHANNELS cannot be 0")
    if channels > len(NON_RESTRICTED_CLIENTS):
        raise ValueError("TOTAL_CHANNELS cannot be greater than number of client fixtures")
    channels_to_test = channels


tokens = TokenGen()
