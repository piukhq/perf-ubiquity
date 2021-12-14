import jwt
import datetime

from locust import HttpUser, SequentialTaskSet, constant, task

from request_data import angelia

from vault import load_secrets
from locust_config import check_suite_whitelist, repeat_task


class UserBehavior(SequentialTaskSet):
    def __init__(self, parent):
        self.email, self.external_id = angelia.generate_random_email_and_sub()
        self.client_name = 'performanceone'
        self.private_key = load_secrets()['api2_private_keys'][self.client_name]
        self.url_prefix = "/v2"
        self.b2b_token = self.generate_b2b_token()
        self.access_token = ""
        self.refresh_token = ""
        super(UserBehavior, self).__init__(parent)

    @task
    def setup_headers(self):
        if not self.private_key:
            self.private_key = load_secrets()

    def generate_b2b_token(self):
        access_life_time = 400
        iat = datetime.datetime.utcnow()
        exp = iat + datetime.timedelta(seconds=access_life_time)

        payload = {"email": self.email, "sub": self.external_id, "iat": iat, "exp": exp}
        headers = {"kid": f"{self.client_name}-2021-12-16"}
        # KIDs have trailing datetime to mimic real KID use cases. We don't need to cycle these so this date can be
        # hardcoded.
        key = self.private_key

        b2b_token = jwt.encode(payload=payload, key=key, algorithm='RS512', headers=headers)

        return b2b_token

    @check_suite_whitelist
    @task
    @repeat_task(2)
    def post_token(self):

        with self.client.post(
            f"{self.url_prefix}/token",
            json={"grant_type": "b2b", "scope": ["user"]},
            headers=f"bearer {self.b2b_token}",
            name=f"{self.url_prefix}/token"
        ) as response:
            data = response.json()
            self.access_token = data["access_token"]
            self.refresh_token = data["refresh_token"]


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = constant(0)
