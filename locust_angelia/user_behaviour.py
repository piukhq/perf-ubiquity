import datetime
import random

import jwt
from locust import SequentialTaskSet
from locust.exception import StopUser
from faker import Faker

from locust_config import MEMBERSHIP_PLANS, repeatable_task
from request_data import angelia
from vault import load_secrets


class UserBehavior(SequentialTaskSet):
    """
    User behaviours for the Angelia performance test suite.
    N.b. Tasks here use a preconfigured 'repeatable_task' decorator, which extends the locust @task decorator and allows
    each task to be run a number of times, as defined in the locustfile which creates this class. All functions to
    be called by the User MUST have the @repeatable_task() decorator, and must also be included in the 'repeats'
    dictionary in the parent locustfile.

    Some terminology:

    'multiuser': used to denote a task performed by a secondary user. This is usually in the case that a user is
    performing an action on a resource which they did not themselves create. E.g. linking to an existing loyalty card or
     payment card account. Unless otherwise stated, this assumes the channel to be the same in all cases.

    'multichannel': effectively used to denote a 'multiuser' task as above, but where the channel is also different.
    """

    def __init__(self, parent):
        self.email, self.external_id = angelia.generate_random_email_and_sub()
        self.client_name = "performanceone"
        self.private_key = load_secrets()["api2_private_keys"][self.client_name]
        self.url_prefix = "/v2"
        self.b2b_tokens = {"primary_user": self.generate_b2b_token(), "secondary_user": self.generate_b2b_token()}
        self.access_tokens = {}
        self.refresh_tokens = {}
        self.loyalty_plan_count = MEMBERSHIP_PLANS
        self.loyalty_cards = []
        self.fake = Faker()
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

        b2b_token = jwt.encode(payload=payload, key=key, algorithm="RS512", headers=headers)

        return b2b_token

    # ---------------------------------TOKEN TASKS---------------------------------

    @repeatable_task()
    def post_token(self):

        with self.client.post(
            f"{self.url_prefix}/token",
            json={"grant_type": "b2b", "scope": ["user"]},
            headers={"Authorization": f"bearer {self.b2b_tokens['primary_user']}"},
            name=f"{self.url_prefix}/token",
        ) as response:
            data = response.json()
            self.access_tokens["primary_user"] = data.get("access_token")
            self.refresh_tokens["primary_user"] = data.get("refresh_token")

    @repeatable_task()
    def post_token_secondary_user(self):

        with self.client.post(
            f"{self.url_prefix}/token",
            json={"grant_type": "b2b", "scope": ["user"]},
            headers={"Authorization": f"bearer {self.b2b_tokens['secondary_user']}"},
            name=f"{self.url_prefix}/token (secondary user)",
        ) as response:
            data = response.json()
            self.access_tokens["secondary_user"] = data.get("access_token")
            self.refresh_tokens["secondary_user"] = data.get("refresh_token")

    @repeatable_task()
    def post_get_new_access_token_via_b2b(self):
        self.post_token()

    @repeatable_task()
    def post_get_new_access_token_via_refresh(self):
        with self.client.post(
            f"{self.url_prefix}/token",
            json={"grant_type": "refresh_token", "scope": ["user"]},
            headers={"Authorization": f"bearer {self.refresh_tokens['primary_user']}"},
            name=f"{self.url_prefix}/token (via refresh)",
        ) as response:
            data = response.json()
            self.access_tokens["primary_user"] = data.get("access_token")
            self.refresh_tokens["primary_user"] = data.get("refresh_token")

    # ---------------------------------LOYALTY PLAN TASKS---------------------------------

    @repeatable_task()
    def get_loyalty_plans(self):
        self.client.get(
            f"{self.url_prefix}/loyalty_plans",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/loyalty_plans",
        )

    @repeatable_task()
    def get_loyalty_plans_by_id(self):
        plan_id = random.choice(range(1, self.loyalty_plan_count))

        self.client.get(
            f"{self.url_prefix}/loyalty_plans/{plan_id}",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/loyalty_plans/[id]",
        )

    @repeatable_task()
    def get_loyalty_plans_journey_fields_by_id(self):
        plan_id = random.choice(range(1, self.loyalty_plan_count))

        self.client.get(
            f"{self.url_prefix}/loyalty_plans/{plan_id}/journey_fields",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/loyalty_plans/[id]/journey_fields",
        )

    @repeatable_task()
    def get_loyalty_plans_overview(self):
        self.client.get(
            f"{self.url_prefix}/loyalty_plans_overview",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/loyalty_plans_overview",
        )

    # ---------------------------------LOYALTY CARD TASKS---------------------------------

    @repeatable_task()
    def post_loyalty_cards_add(self):

        # ADD with primary user - creates new card

        plan_id = random.choice(range(1, self.loyalty_plan_count))

        data = {
            "loyalty_plan_id": plan_id,
            "account": {
                "add_fields": {
                    "credentials": [{"credential_slug": "card_number", "value": str(random.randint(100000, 1000000))}]
                }
            },
        }

        with self.client.post(
            f"{self.url_prefix}/loyalty_cards/add",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/loyalty_cards/add",
            json=data,
        ) as response:
            loyalty_card_id = response.json()["id"]

        self.loyalty_cards.append({"loyalty_card_id": loyalty_card_id, "data": data})

        #  ADD with secondary user (Multiuser) - links secondary user to just-created card

        with self.client.post(
            f"{self.url_prefix}/loyalty_cards/add",
            headers={"Authorization": f"bearer {self.access_tokens['secondary_user']}"},
            name=f"{self.url_prefix}/loyalty_cards/add (MULTIUSER)",
            json=data,
        ) as response:
            loyalty_card_id = response.json()["id"]
            if loyalty_card_id not in [item["loyalty_card_id"] for item in self.loyalty_cards]:
                response.failure()

    @repeatable_task()
    def post_loyalty_cards_add_and_auth(self):

        # ADD_AND_AUTH with primary user - creates new card

        plan_id = random.choice(range(1, self.loyalty_plan_count))

        data = {
            "loyalty_plan_id": plan_id,
            "account": {
                "add_fields": {
                    "credentials": [{"credential_slug": "card_number", "value": self.fake.credit_card_number()}]
                },
                "authorise_fields": {
                    "credentials": [
                        {"credential_slug": "password", "value": self.fake.password()}],
                    "consents": [{
                        "consent_slug": f"consent_slug_{plan_id}",
                        "value": "true"
                    }]
                }
            },
        }

        with self.client.post(
                f"{self.url_prefix}/loyalty_cards/add_and_authorise",
                headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
                name=f"{self.url_prefix}/loyalty_cards/add_and_authorise",
                json=data,
        ) as response:
            loyalty_card_id = response.json()["id"]

        self.loyalty_cards.append({"loyalty_card_id": loyalty_card_id, "data": data})

        #  ADD with secondary user (Multiuser) - links secondary user to just-created card

        with self.client.post(
                f"{self.url_prefix}/loyalty_cards/add_and_authorise",
                headers={"Authorization": f"bearer {self.access_tokens['secondary_user']}"},
                name=f"{self.url_prefix}/loyalty_cards/add_and_authorise (MULTIUSER)",
                json=data,
        ) as response:
            loyalty_card_id = response.json()["id"]
            if loyalty_card_id not in [item["loyalty_card_id"] for item in self.loyalty_cards]:
                response.failure()

    @repeatable_task()
    def post_loyalty_cards_join(self):

        # JOIN only with primary user

        plan_id = random.choice(range(1, self.loyalty_plan_count))

        data = {
            "loyalty_plan_id": plan_id,
            "account": {
                "join_fields": {
                    "credentials": [
                        {"credential_slug": "card_number", "value": self.fake.credit_card_number()},
                        {"credential_slug": "password", "value": self.fake.password()}],
                }
            },
        }

        self.client.post(
                f"{self.url_prefix}/loyalty_cards/join",
                headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
                name=f"{self.url_prefix}/loyalty_cards/join",
                json=data,
        )

    @repeatable_task()
    def delete_loyalty_card_by_id(self):

        if self.loyalty_cards:
            card_id = self.loyalty_cards[0]['loyalty_card_id']
        else:
            card_id = 'NO_CARD'

        with self.client.delete(
            f"{self.url_prefix}/loyalty_cards/{card_id}",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/loyalty_cards/[id]",
        ):
            self.loyalty_cards.pop(0)

    # ---------------------------------USER TASKS---------------------------------

    @repeatable_task()
    def delete_me(self):
        self.client.delete(
            f"{self.url_prefix}/me",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/me",
        )

    # ---------------------------------SPECIAL TASKS---------------------------------

    @repeatable_task()
    def stop_locust_after_test_suite(self):
        raise StopUser()
