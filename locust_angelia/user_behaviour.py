import json
import logging
import random

import redis
from faker import Faker
from locust import SequentialTaskSet
from locust.exception import StopUser

import settings
from locust_config import MEMBERSHIP_PLANS, repeatable_task

logger = logging.getLogger(__name__)
r = redis.from_url(settings.REDIS_URL)


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
        super().__init__(parent)
        self.url_prefix = "/v2"
        self.b2b_tokens = {}
        self.access_tokens = {}
        self.refresh_tokens = {}
        self.loyalty_plan_count = MEMBERSHIP_PLANS
        self.loyalty_cards = {}
        self.fake = Faker()

    # ---------------------------------TOKEN TASKS---------------------------------

    def on_start(self):
        try:
            self.get_tokens()
        except Exception:
            logger.error("Failed to get b2b_tokens from Redis for this user. Stopping User.")
            raise StopUser()

    def get_tokens(self):
        tokens = json.loads(r.lpop("user_tokens"))
        print(tokens)
        self.b2b_tokens = tokens

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
                    "credentials": [{"credential_slug": "card_number", "value": self.fake.credit_card_number()}]
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

        self.loyalty_cards.update({loyalty_card_id: {"data": data, "state": "ADD", "plan_id": plan_id}})
        print(self.loyalty_cards)

        #  ADD with secondary user (Multiuser) - links secondary user to just-created card

        with self.client.post(
            f"{self.url_prefix}/loyalty_cards/add",
            headers={"Authorization": f"bearer {self.access_tokens['secondary_user']}"},
            name=f"{self.url_prefix}/loyalty_cards/add (MULTIUSER)",
            json=data,
        ) as response:
            loyalty_card_id = response.json()["id"]
            if response.json()["id"] != loyalty_card_id:
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
                    "credentials": [{"credential_slug": "password", "value": self.fake.password()}],
                    "consents": [{"consent_slug": f"consent_slug_{plan_id}", "value": "true"}],
                },
            },
        }

        with self.client.post(
            f"{self.url_prefix}/loyalty_cards/add_and_authorise",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/loyalty_cards/add_and_authorise",
            json=data,
        ) as response:
            loyalty_card_id = response.json()["id"]

            self.loyalty_cards.update(loyalty_card_id={"data": data, "state": "AUTH", "plan_id": plan_id})

        #  ADD_AND_AUTH with secondary user (Multiuser) - links secondary user to just-created card

        with self.client.post(
            f"{self.url_prefix}/loyalty_cards/add_and_authorise",
            headers={"Authorization": f"bearer {self.access_tokens['secondary_user']}"},
            name=f"{self.url_prefix}/loyalty_cards/add_and_authorise (MULTIUSER)",
            json=data,
        ) as response:
            if response.json()["id"] != loyalty_card_id:
                response.failure()

    @repeatable_task()
    def put_loyalty_cards_authorise(self):
        """
        For each request:
        1. Tries to get a random previously added card that hasn't yet been registered or authed (-> 202).
        2. If not, tries to get a random previously added card that has already been authed (-> 200).
        3. Else, will return a 404.
        """

        # AUTHORISE with primary user

        card_id = None

        if self.loyalty_cards:
            print(self.loyalty_cards.keys())
            add_card_ids = [
                card_id for card_id in self.loyalty_cards.keys() if self.loyalty_cards[card_id]["state"] == "ADD"
            ]
            print("ADD_CARD_IDS" + str(add_card_ids[0]))
            if add_card_ids:
                card_id = random.choice(add_card_ids)
            else:
                auth_card_ids = [
                    card_id for card_id in self.loyalty_cards.keys() if self.loyalty_cards[card_id]["state"] == "AUTH"
                ]
                if auth_card_ids:
                    card_id = random.choice(auth_card_ids)

        if card_id:
            plan_id = self.loyalty_cards[card_id]["plan_id"]
        else:
            card_id = "MISSING_CARD_404"
            plan_id = random.choice(range(1, self.loyalty_plan_count))

        data = {
            "account": {
                "authorise_fields": {
                    "credentials": [{"credential_slug": "password", "value": self.fake.password()}],
                    "consents": [{"consent_slug": f"consent_slug_{plan_id}", "value": "true"}],
                },
            },
        }

        print(card_id)

        with self.client.put(
            f"{self.url_prefix}/loyalty_cards/authorise/{card_id}",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/loyalty_cards/authorise/[id]",
            json=data,
        ) as response:
            if response.json()["id"] == card_id:
                self.loyalty_cards[card_id]["state"] = "AUTH"  # Set State so /register doesn't try to use this card.
            else:
                response.failure()

    @repeatable_task()
    def post_loyalty_cards_add_and_register(self):

        # ADD_AND_REGISTER with primary user - creates new card

        plan_id = random.choice(range(1, self.loyalty_plan_count))

        data = {
            "loyalty_plan_id": plan_id,
            "account": {
                "add_fields": {
                    "credentials": [{"credential_slug": "card_number", "value": self.fake.credit_card_number()}]
                },
                "register_ghost_card_fields": {
                    "credentials": [{"credential_slug": "password", "value": self.fake.password()}],
                    "consents": [],
                },
            },
        }

        with self.client.post(
            f"{self.url_prefix}/loyalty_cards/add_and_register",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/loyalty_cards/add_and_register",
            json=data,
        ) as response:
            loyalty_card_id = response.json()["id"]

            self.loyalty_cards.update(loyalty_card_id={"data": data, "state": "REG", "plan_id": plan_id})

        #  ADD_AND_REGISTER with secondary user (Multiuser) - links secondary user to just-created card

        with self.client.post(
            f"{self.url_prefix}/loyalty_cards/add_and_register",
            headers={"Authorization": f"bearer {self.access_tokens['secondary_user']}"},
            name=f"{self.url_prefix}/loyalty_cards/add_and_register (MULTIUSER)",
            json=data,
        ) as response:
            if response.json()["id"] != loyalty_card_id:
                response.failure()

    @repeatable_task()
    def post_loyalty_cards_register(self):

        # REGISTER with primary user

        if self.loyalty_cards:
            random_id = random.choice(
                [card_id for card_id in self.loyalty_cards.keys() if self.loyalty_cards[card_id]["state"] == "ADD"]
            )
            existing_loyalty_card = self.loyalty_cards[random_id]
            plan_id = existing_loyalty_card["plan_id"]
            card_id = existing_loyalty_card["loyalty_card_id"]
        else:
            card_id = "MISSING_CARD_404"
            plan_id = random.choice(range(1, self.loyalty_plan_count))

        data = {
            "account": {
                "authorise_fields": {
                    "credentials": [{"credential_slug": "password", "value": self.fake.password()}],
                    "consents": [{"consent_slug": f"consent_slug_{plan_id}", "value": "true"}],
                },
            },
        }

        with self.client.post(
            f"{self.url_prefix}/loyalty_cards/authorise/{card_id}",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/loyalty_cards/authorise/[id]",
            json=data,
        ) as response:
            if response.json()["id"] == card_id:
                self.loyalty_cards[card_id]["state"] = "REG"  # Set State so /register doesn't try to use this card.
            else:
                response.failure()

    @repeatable_task()
    def delete_loyalty_card_by_id(self):

        if self.loyalty_cards:
            card_id = list(self.loyalty_cards.keys())[0]
        else:
            card_id = "NO_CARD"

        with self.client.delete(
            f"{self.url_prefix}/loyalty_cards/{card_id}",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/loyalty_cards/[id]",
        ):
            self.loyalty_cards.pop(card_id)

    # ---------------------------------WALLET TASKS---------------------------------

    @repeatable_task()
    def get_wallet(self):

        self.client.delete(
                f"{self.url_prefix}/wallet",
                headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
                name=f"{self.url_prefix}/wallet",
        )

    @repeatable_task()
    def get_wallet_overview(self):

        self.client.delete(
            f"{self.url_prefix}/wallet_overview",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/wallet_overview",
        )

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
