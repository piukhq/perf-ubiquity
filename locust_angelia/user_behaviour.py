import random

import jwt
import datetime
from locust.exception import StopUser

from locust import HttpUser, SequentialTaskSet, constant

from request_data import angelia

from vault import load_secrets
from locust_config import check_suite_whitelist, repeatable_task


class UserBehavior(SequentialTaskSet):
    """
    User behaviours for the Angelia performance test suite.
    N.b. Tasks here use a preconfigured 'repeatable_task' decorator, which extends the locust @task decorator and allows
    each task to be repeated a number of times, as defined in the locustfile which creates this class. All functions to
    be called by the User MUST have the @repeatable_task() decorator. Any function with this decorator which is not
    explicitly defined in the locustfile will default to one execution.
    """

    def __init__(self, parent):
        self.email, self.external_id = angelia.generate_random_email_and_sub()
        self.client_name = 'performanceone'
        self.private_key = load_secrets()['api2_private_keys'][self.client_name]
        self.url_prefix = "/v2"
        self.b2b_token = self.generate_b2b_token()
        self.access_token = ""
        self.refresh_token = ""
        super(UserBehavior, self).__init__(parent)

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
    @repeatable_task()
    def post_token(self):

        with self.client.post(
            f"{self.url_prefix}/token",
            json={"grant_type": "b2b", "scope": ["user"]},
            headers={"Authorization": f"bearer {self.b2b_token}"},
            name=f"{self.url_prefix}/token"
        ) as response:
            data = response.json()
            self.access_token = data["access_token"]
            self.refresh_token = data["refresh_token"]

    @check_suite_whitelist
    @repeatable_task()
    def get_new_token(self):

        token_task = random.choice([self.post_token_refresh, self.post_token])
        token_task()

    def post_token_refresh(self):
        with self.client.post(
                f"{self.url_prefix}/token",
                json={"grant_type": "refresh_token", "scope": ["user"]},
                headers={"Authorization": f"bearer {self.refresh_token}"},
                name=f"{self.url_prefix}/token (refresh)"
        ) as response:
            data = response.json()
            self.access_token = data["access_token"]
            self.refresh_token = data["refresh_token"]

    @check_suite_whitelist
    @repeatable_task()
    def stop_locust_after_test_suite(self):
        raise StopUser()


class WebsiteUser(HttpUser):

    load_secrets()
    tasks = [UserBehavior]
    wait_time = constant(0)

