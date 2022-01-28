import datetime

import jwt

from request_data import angelia
from vault import load_secrets

user_count = 0


class TokenGen:
    def __init__(self):
        self.all_user_tokens = []

    def generate_tokens(self, environment):
        print("generating tokens")

        total_users = environment.runner.target_user_count

        for i in range(total_users):
            user_tokens = self.generate_b2b_tokens()
            self.all_user_tokens.append(user_tokens)

    @staticmethod
    def setup_user_info():
        data = {}
        for user in ["primary_user", "secondary_user"]:
            email, external_id = angelia.generate_random_email_and_sub()
            data[user] = {}
            data[user]["email"] = email
            data[user]["external_id"] = external_id
        return data

    def generate_b2b_tokens(self):
        client_name = "performanceone"
        private_key = load_secrets()["api2_private_keys"][client_name]
        b2b_tokens = {}
        user_details = self.setup_user_info()

        for user in ["primary_user", "secondary_user"]:

            access_life_time = 400
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
            key = private_key

            b2b_token = jwt.encode(payload=payload, key=key, algorithm="RS512", headers=headers)

            b2b_tokens[user] = b2b_token

        return b2b_tokens


def reset_tokens():
    global all_user_tokens
    all_user_tokens = None


tokens = TokenGen()
