import json
import random
import time
import uuid
from copy import deepcopy

from faker import Faker
from locust import SequentialTaskSet
from locust.exception import StopUser
from loguru import logger

from ubiquity_performance_test.config import redis
from ubiquity_performance_test.locust_angelia.database.jobs import query_status, set_status_for_loyalty_card
from ubiquity_performance_test.locust_config import MEMBERSHIP_PLANS, repeatable_task

retry_time: float = 0.0
timeout: float = 0.0


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

    def __init__(self, parent: type[SequentialTaskSet]) -> None:
        super().__init__(parent)
        self.url_prefix = "/v2"
        self.b2b_tokens: dict = {}
        self.access_tokens: dict = {}
        self.refresh_tokens: dict = {}
        self.loyalty_plan_count = MEMBERSHIP_PLANS
        self.loyalty_cards: dict = {}
        self.trusted_loyalty_cards: dict = {}
        self.join_ids: list = []
        self.payment_cards: dict = {}
        self.trusted_channel_payment_cards: dict = {}
        self.fake = Faker()

    # ---------------------------------TOKEN TASKS---------------------------------

    def on_start(self) -> None:
        try:
            self.get_tokens()
        except Exception:
            logger.error("Failed to get b2b_tokens from Redis for this user. Stopping User.")
            raise StopUser() from None

    def get_tokens(self) -> None:
        tokens = json.loads(redis.lpop("user_tokens"))
        logger.info(f"User tokens: {tokens}")
        self.b2b_tokens = tokens

    @repeatable_task()
    def post_token(self) -> None:
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
    def post_token_secondary_user(self) -> None:
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
    def post_token_trusted_channel_primary_user(self) -> None:
        # Remove this extra pre-call when bug to fix first token not being trusted has been fixed
        self.client.post(
            f"{self.url_prefix}/token",
            json={"grant_type": "b2b", "scope": ["user"]},
            headers={"Authorization": f"bearer {self.b2b_tokens['trusted_channel_primary_user']}"},
            name=f"{self.url_prefix}/token",
        )

        with self.client.post(
            f"{self.url_prefix}/token",
            json={"grant_type": "b2b", "scope": ["user"]},
            headers={"Authorization": f"bearer {self.b2b_tokens['trusted_channel_primary_user']}"},
            name=f"{self.url_prefix}/token",
        ) as response:
            data = response.json()
            self.access_tokens["trusted_channel_primary_user"] = data.get("access_token")
            self.refresh_tokens["trusted_channel_primary_user"] = data.get("refresh_token")

    @repeatable_task()
    def post_token_trusted_channel_secondary_user(self) -> None:
        # Remove this extra pre-call when bug to fix first token not being trusted has been fixed
        self.client.post(
            f"{self.url_prefix}/token",
            json={"grant_type": "b2b", "scope": ["user"]},
            headers={"Authorization": f"bearer {self.b2b_tokens['trusted_channel_secondary_user']}"},
            name=f"{self.url_prefix}/token",
        )

        with self.client.post(
            f"{self.url_prefix}/token",
            json={"grant_type": "b2b", "scope": ["user"]},
            headers={"Authorization": f"bearer {self.b2b_tokens['trusted_channel_secondary_user']}"},
            name=f"{self.url_prefix}/token",
        ) as response:
            data = response.json()
            self.access_tokens["trusted_channel_secondary_user"] = data.get("access_token")
            self.refresh_tokens["trusted_channel_secondary_user"] = data.get("refresh_token")

    @repeatable_task()
    def post_get_new_access_token_via_refresh(self) -> None:
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
    def get_loyalty_plans(self) -> None:
        self.client.get(
            f"{self.url_prefix}/loyalty_plans",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/loyalty_plans",
        )

    @repeatable_task()
    def get_loyalty_plans_by_id(self) -> None:
        plan_id = random.choice(range(1, self.loyalty_plan_count))

        self.client.get(
            f"{self.url_prefix}/loyalty_plans/{plan_id}",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/loyalty_plans/[id]",
        )

    @repeatable_task()
    def get_loyalty_plan_details_by_id(self) -> None:
        plan_id = random.choice(range(1, self.loyalty_plan_count))

        self.client.get(
            f"{self.url_prefix}/loyalty_plans/{plan_id}/plan_details",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/loyalty_plans/[id]/plan_details",
        )

    @repeatable_task()
    def get_loyalty_plans_journey_fields_by_id(self) -> None:
        plan_id = random.choice(range(1, self.loyalty_plan_count))

        self.client.get(
            f"{self.url_prefix}/loyalty_plans/{plan_id}/journey_fields",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/loyalty_plans/[id]/journey_fields",
        )

    @repeatable_task()
    def get_loyalty_plans_overview(self) -> None:
        self.client.get(
            f"{self.url_prefix}/loyalty_plans_overview",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/loyalty_plans_overview",
        )

    # ---------------------------------LOYALTY CARD TASKS---------------------------------

    @repeatable_task()
    def post_loyalty_cards_add(self) -> None:
        """POSTS an add request."""

        # ADD with primary user - creates new card

        plan_id = random.choice(range(1, self.loyalty_plan_count))

        data = {
            "loyalty_plan_id": plan_id,
            "account": {
                "add_fields": {
                    "credentials": [{"credential_slug": "card_number", "value": "3" + self.fake.credit_card_number()}]
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
    def post_loyalty_cards_add_trusted(self) -> None:
        """POSTS a trusted channel add request."""

        # ADD_AND_AUTH with primary user - creates new card

        plan_id = random.choice(range(1, self.loyalty_plan_count))
        logger.info(f"Access tokens before trusted channel POST: {self.access_tokens}")

        data = {
            "loyalty_plan_id": plan_id,
            "account": {
                "add_fields": {
                    "credentials": [{"credential_slug": "card_number", "value": "3" + self.fake.credit_card_number()}]
                },
                "merchant_fields": {"account_id": str(uuid.uuid4())},
            },
        }

        with self.client.post(
            f"{self.url_prefix}/loyalty_cards/add_trusted",
            headers={"Authorization": f"bearer {self.access_tokens['trusted_channel_primary_user']}"},
            name=f"{self.url_prefix}/loyalty_cards/add_trusted",
            json=data,
        ) as response:
            loyalty_card_id = response.json()["id"]
            self.trusted_loyalty_cards.update(
                {loyalty_card_id: {"data": data, "state": "TRUSTED_ADD", "plan_id": plan_id}}
            )

        #  ADD with secondary user (Multiuser) - links secondary user to just-created card

        with self.client.post(
            f"{self.url_prefix}/loyalty_cards/add_trusted",
            headers={"Authorization": f"bearer {self.access_tokens['trusted_channel_secondary_user']}"},
            name=f"{self.url_prefix}/loyalty_cards/add_trusted (MULTIUSER)",
            json=data,
        ) as response:
            loyalty_card_id = response.json()["id"]
            if response.json()["id"] != loyalty_card_id:
                response.failure()

    @repeatable_task()
    def post_loyalty_cards_add_and_auth(self) -> None:
        """POSTS an add_and_auth request."""

        # ADD_AND_AUTH with primary user - creates new card

        plan_id = random.choice(range(1, self.loyalty_plan_count))

        data = {
            "loyalty_plan_id": plan_id,
            "account": {
                "add_fields": {
                    "credentials": [{"credential_slug": "card_number", "value": "3" + self.fake.credit_card_number()}]
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

            self.loyalty_cards.update({loyalty_card_id: {"data": data, "state": "AUTH", "plan_id": plan_id}})

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
    def put_loyalty_cards_authorise(self) -> None:
        """
        For each request:
        1. Tries to get a random previously added card that hasn't yet been registered or authed (-> 202).
        2. If not, tries to get a random previously added card that has already been authed (-> 200).
        3. Else, will return a 404.
        """

        card_id = None

        if self.loyalty_cards:
            add_card_ids = [card_id for card_id in self.loyalty_cards if self.loyalty_cards[card_id]["state"] == "ADD"]
            if add_card_ids:
                card_id = random.choice(add_card_ids)
            else:
                auth_card_ids = [
                    card_id for card_id in self.loyalty_cards if self.loyalty_cards[card_id]["state"] == "AUTH"
                ]
                if auth_card_ids:
                    card_id = random.choice(auth_card_ids)

        if card_id:
            plan_id = self.loyalty_cards[card_id]["plan_id"]
            card_number = self.loyalty_cards[card_id]["data"]["account"]["add_fields"]["credentials"][0]["value"]
        else:
            card_id = "MISSING_CARD_404"
            plan_id = ""
            card_number = ""

        data = {
            "account": {
                "add_fields": {"credentials": [{"credential_slug": "card_number", "value": card_number}]},
                "authorise_fields": {
                    "credentials": [{"credential_slug": "password", "value": self.fake.password()}],
                    "consents": [{"consent_slug": f"consent_slug_{plan_id}", "value": "true"}],
                },
            },
        }

        with self.client.put(
            f"{self.url_prefix}/loyalty_cards/{card_id}/authorise",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/loyalty_cards/[id]/authorise",
            json=data,
        ) as response:
            if response.json()["id"] == card_id:
                self.loyalty_cards[card_id]["state"] = "AUTH"  # Set State so /register doesn't try to use this card.
            else:
                response.failure()

    @repeatable_task()
    def put_loyalty_cards_trusted_channel(self) -> None:
        """
        For each request:
        1. Tries to get a random previously added card that hasn't yet been registered or authed (-> 202).
        2. If not, tries to get a random previously added card that has already been authed (-> 200).
        3. Else, will return a 404.
        """

        card_id = random.choice(list(self.trusted_loyalty_cards.keys()))

        data = {
            "account": {
                "add_fields": {
                    "credentials": [{"credential_slug": "card_number", "value": "3" + self.fake.credit_card_number()}]
                },
                "merchant_fields": {"account_id": str(uuid.uuid4())},
            }
        }

        with self.client.put(
            f"{self.url_prefix}/loyalty_cards/{card_id}/add_trusted",
            headers={"Authorization": f"bearer {self.access_tokens['trusted_channel_primary_user']}"},
            name=f"{self.url_prefix}/loyalty_cards/[id]/authorise",
            json=data,
        ) as response:
            if response.json()["id"] != card_id:
                self.trusted_loyalty_cards[card_id]["state"] = "TRUSTED_PUT"
            else:
                response.failure()

    @repeatable_task()
    def post_loyalty_cards_add_and_register(self) -> None:
        """POSTS an add_and_register request."""

        plan_id = random.choice(range(1, self.loyalty_plan_count))

        data = {
            "loyalty_plan_id": plan_id,
            "account": {
                "add_fields": {
                    "credentials": [{"credential_slug": "card_number", "value": "3" + self.fake.credit_card_number()}]
                },
                "register_ghost_card_fields": {
                    "credentials": [
                        {"credential_slug": "password", "value": self.fake.password()},
                        {"credential_slug": "first_name", "value": (self.fake.first_name())},
                    ],
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

            self.loyalty_cards.update({loyalty_card_id: {"data": data, "state": "REG", "plan_id": plan_id}})

    @repeatable_task()
    def put_loyalty_cards_register(self) -> None:
        """PUTs a Register request for a (randomly selected) previously added card. If no remaining ADD card exists
        then will 404."""

        card_id = None
        if self.loyalty_cards:
            add_card_ids = [card_id for card_id in self.loyalty_cards if self.loyalty_cards[card_id]["state"] == "ADD"]
            if add_card_ids:
                card_id = random.choice(add_card_ids)

        card_id = card_id or "NOT_FOUND"

        data = {
            "account": {
                "register_ghost_card_fields": {
                    "credentials": [
                        {"credential_slug": "password", "value": self.fake.password()},
                        {"credential_slug": "first_name", "value": (self.fake.first_name())},
                    ],
                    "consents": [],
                },
            },
        }

        with self.client.put(
            f"{self.url_prefix}/loyalty_cards/{card_id}/register",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/loyalty_cards/[id]/register",
            json=data,
        ) as response:
            if response.json()["id"] == card_id:
                self.loyalty_cards[card_id]["state"] = "REG"  # Set State so /authorise doesn't try to use this card.
            else:
                response.failure()

    @repeatable_task()
    def post_loyalty_cards_join(self) -> None:
        """POSTS a join request."""

        plan_id = random.choice(range(1, self.loyalty_plan_count))

        data = {
            "loyalty_plan_id": plan_id,
            "account": {
                "join_fields": {
                    "credentials": [
                        {"credential_slug": "first_name", "value": (self.fake.first_name())},
                        {"credential_slug": "password", "value": (self.fake.password() + "_failure")},
                        # the 'failure' keyword means that all joins will become failed joins in Midas mock agents.
                        # This is so that we can test deleting failed joins later down the line (otherwise these go into
                        # pending state which we can't delete!
                    ]
                }
            },
        }

        with self.client.post(
            f"{self.url_prefix}/loyalty_cards/join",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/loyalty_cards/join",
            json=data,
        ) as response:
            loyalty_card_id = response.json()["id"]

        self.join_ids.append(loyalty_card_id)

    @repeatable_task()
    def put_loyalty_cards_join(self) -> None:
        """
        PUT request an existing loyalty card join. Will 404 if no joins available or 409 if not in failed state.
        """

        plan_id = random.choice(range(1, self.loyalty_plan_count))
        join_ids = deepcopy(self.join_ids)

        if join_ids:
            card_id = join_ids.pop(0)
            set_status_for_loyalty_card(card_id, 901)
        else:
            card_id = "NO_CARD"

        data = {
            "loyalty_plan_id": plan_id,
            "account": {
                "join_fields": {
                    "credentials": [
                        {"credential_slug": "first_name", "value": (self.fake.first_name())},
                        {"credential_slug": "password", "value": (self.fake.password() + "_failure")},
                        # the 'failure' keyword means that all joins will become failed joins in Midas mock agents.
                        # This is so that we can test deleting failed joins later down the line (otherwise these go into
                        # pending state which we can't delete!
                    ]
                }
            },
        }

        self.client.put(
            f"{self.url_prefix}/loyalty_cards/{card_id}/join",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/loyalty_cards/[id]/join",
            json=data,
        )

    @repeatable_task()
    def get_loyalty_cards_balance(self) -> None:
        card_id = random.choice(list(self.loyalty_cards.keys())) if self.loyalty_cards else "NO CARD"

        self.client.get(
            f"{self.url_prefix}/loyalty_cards/{card_id}/balance",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/loyalty_cards/[id]/balance",
        )

    @repeatable_task()
    def get_loyalty_cards_transactions(self) -> None:
        card_id = random.choice(list(self.loyalty_cards.keys())) if self.loyalty_cards else "NO CARD"

        self.client.get(
            f"{self.url_prefix}/loyalty_cards/{card_id}/transactions",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/loyalty_cards/[id]/transactions",
        )

    @repeatable_task()
    def get_loyalty_cards_vouchers(self) -> None:
        card_id = random.choice(list(self.loyalty_cards.keys())) if self.loyalty_cards else "NO CARD"

        self.client.get(
            f"{self.url_prefix}/loyalty_cards/{card_id}/vouchers",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/loyalty_cards/[id]/vouchers",
        )

    # ---------------------------------PAYMENT ACCOUNT TASKS---------------------------------

    @repeatable_task()
    def post_payment_account(self) -> None:
        """POSTs a new Payment account. Both Single and Multiuser. Randomly selects between Visa, Amex and Mastercard"""

        # Single-User POST

        card_nickname = self.fake.pystr()

        data = {
            "expiry_month": self.fake.month(),
            "expiry_year": self.fake.year(),
            "name_on_card": self.fake.name(),
            "card_nickname": card_nickname,
            "issuer": "HSBC",
            "token": str(uuid.uuid4()),
            "last_four_digits": str(random.randint(1000, 9999)),
            "first_six_digits": random.choice(["444444", "222155", "343434"]),
            "fingerprint": str(uuid.uuid4()),
            "type": "debit",
            "country": "GB",
            "currency_code": "GBP",
        }

        with self.client.post(
            f"{self.url_prefix}/payment_accounts",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/payment_accounts",
            json=data,
        ) as response:
            payment_account_id = response.json()["id"]
            self.payment_cards.update({payment_account_id: {"data": data}})

        # Multi-User POST

        with self.client.post(
            f"{self.url_prefix}/payment_accounts",
            headers={"Authorization": f"bearer {self.access_tokens['secondary_user']}"},
            name=f"{self.url_prefix}/payment_accounts (MULTIUSER)",
            json=data,
        ) as response:
            multiuser_payment_account_id = response.json()["id"]
            if multiuser_payment_account_id != payment_account_id:
                response.failure()

    @repeatable_task()
    def post_payment_account_trusted_channel_user(self) -> None:
        """POSTs a new Payment account for a trusted channel user. Randomly selects between Visa, Amex and Mastercard"""

        # Single-User POST

        card_nickname = self.fake.pystr()
        data = {
            "expiry_month": self.fake.month(),
            "expiry_year": self.fake.year(),
            "name_on_card": self.fake.name(),
            "card_nickname": card_nickname,
            "issuer": "HSBC",
            "token": str(uuid.uuid4()),
            "last_four_digits": str(random.randint(1000, 9999)),
            "first_six_digits": random.choice(["444444", "222155", "343434"]),
            "fingerprint": str(uuid.uuid4()),
            "type": "debit",
            "country": "GB",
            "currency_code": "GBP",
        }

        with self.client.post(
            f"{self.url_prefix}/payment_accounts",
            headers={"Authorization": f"bearer {self.access_tokens['trusted_channel_primary_user']}"},
            name=f"{self.url_prefix}/payment_accounts",
            json=data,
        ) as response:
            payment_account_id = response.json()["id"]
            self.trusted_channel_payment_cards.update({payment_account_id: {"data": data}})

        # Multi-User POST

        with self.client.post(
            f"{self.url_prefix}/payment_accounts",
            headers={"Authorization": f"bearer {self.access_tokens['trusted_channel_secondary_user']}"},
            name=f"{self.url_prefix}/payment_accounts (MULTIUSER)",
            json=data,
        ) as response:
            multiuser_payment_account_id = response.json()["id"]
            if multiuser_payment_account_id != payment_account_id:
                response.failure()

    @repeatable_task()
    def patch_payment_account(self) -> None:
        """PATCHes a random payment account with a new card_nickname, one of the fields which will correctly trigger a
        Payment Account PATCH. If no payment account is found, this will 404."""

        if self.payment_cards:
            payment_account_id = random.choice(list(self.payment_cards.keys()))

            new_nickname = self.fake.pystr()

        else:
            payment_account_id = "NOT_FOUND"
            new_nickname = ""

        data = {"card_nickname": new_nickname}

        with self.client.patch(
            f"{self.url_prefix}/payment_accounts/{payment_account_id}",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/payment_accounts/[id]",
            json=data,
        ) as response:
            response_payment_account_id = response.json()["id"]
            if response_payment_account_id != payment_account_id:
                response.failure()

    # ---------------------------------WALLET TASKS---------------------------------

    @repeatable_task()
    def get_wallet(self) -> None:
        self.client.get(
            f"{self.url_prefix}/wallet",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/wallet",
        )

    @repeatable_task()
    def get_wallet_trusted_channel(self) -> None:
        self.client.get(
            f"{self.url_prefix}/wallet",
            headers={"Authorization": f"bearer {self.access_tokens['trusted_channel_primary_user']}"},
            name=f"{self.url_prefix}/wallet",
        )

    @repeatable_task()
    def get_wallet_overview(self) -> None:
        self.client.get(
            f"{self.url_prefix}/wallet_overview",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/wallet_overview",
        )

    @repeatable_task()
    def get_wallet_overview_trusted_channel(self) -> None:
        self.client.get(
            f"{self.url_prefix}/wallet_overview",
            headers={"Authorization": f"bearer {self.access_tokens['trusted_channel_primary_user']}"},
            name=f"{self.url_prefix}/wallet_overview",
        )

    @repeatable_task()
    def get_trusted_channel_payment_account_channel_links(self) -> None:
        self.client.get(
            f"{self.url_prefix}/wallet/payment_account_channel_links",
            headers={"Authorization": f"bearer {self.access_tokens['trusted_channel_primary_user']}"},
            name=f"{self.url_prefix}/wallet/payment_account_channel_links",
        )

    @repeatable_task()
    def get_wallet_loyalty_card(self) -> None:
        card_id = random.choice(list(self.loyalty_cards.keys())) if self.loyalty_cards else "NO_CARD"

        self.client.get(
            f"{self.url_prefix}/wallet/loyalty_cards/{card_id}",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/wallet/loyalty_cards/[id]",
        )

    # ---------------------------------DELETE TASKS---------------------------------
    # These are separated from other loyalty account/ payment account functions because they are performed
    # asynchronously, and so risk creating race conditions on the wallet/retrieval endpoints.

    @repeatable_task()
    def delete_join(self) -> None:
        """DELETEs an existing loyalty card join. Will 404 if no joins available."""

        current_retry = 0.0

        if self.join_ids:
            card_id = self.join_ids.pop(0)
            while current_retry < timeout:
                if 901 in query_status(card_id):  # 901 = ENROL_FAILED
                    break
                else:
                    time.sleep(retry_time)
                    current_retry += retry_time
            if current_retry >= timeout:
                logger.error(
                    f"STATUS TIMEOUT: Loyalty Card {card_id} still not processed after {timeout} seconds. Sending "
                    f"request anyway."
                )
        else:
            card_id = "NO_CARD"

        self.client.delete(
            f"{self.url_prefix}/loyalty_cards/{card_id}/join",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/loyalty_cards/[id]/join",
        )

    @repeatable_task()
    def delete_loyalty_card(self) -> None:
        """DELETEs an existing loyalty card. Will 404 if no cards available."""

        card_id = list(self.loyalty_cards.keys())[0] if self.loyalty_cards else "NO_CARD"

        with self.client.delete(
            f"{self.url_prefix}/loyalty_cards/{card_id}",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/loyalty_cards/[id]",
        ):
            self.loyalty_cards.pop(card_id)

    @repeatable_task()
    def delete_trusted_loyalty_card(self) -> None:
        """DELETEs an existing loyalty card from a trusted channel user. Will 404 if no cards available."""

        card_id = list(self.trusted_loyalty_cards.keys())[0] if self.trusted_loyalty_cards else "NO_CARD"

        with self.client.delete(
            f"{self.url_prefix}/loyalty_cards/{card_id}",
            headers={"Authorization": f"bearer {self.access_tokens['trusted_channel_primary_user']}"},
            name=f"{self.url_prefix}/loyalty_cards/[id]",
        ):
            self.trusted_loyalty_cards.pop(card_id)

    @repeatable_task()
    def delete_payment_account(self) -> None:
        """DELETEs a random payment account. If none are present, this will 404."""

        if self.payment_cards:
            payment_account_id = random.choice(list(self.payment_cards.keys()))
            self.payment_cards.pop(payment_account_id)

        else:
            payment_account_id = "NOT_FOUND"

        self.client.delete(
            f"{self.url_prefix}/payment_accounts/{payment_account_id}",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/payment_accounts/[id]",
        )

    # ---------------------------------USER TASKS---------------------------------

    @repeatable_task()
    def post_email_update(self) -> None:
        data = {"email": "updated-" + str(uuid.uuid4()) + "@testbink.com"}

        self.client.post(
            f"{self.url_prefix}/email_update",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/email_update",
            json=data,
        )

    @repeatable_task()
    def delete_me(self) -> None:
        self.client.delete(
            f"{self.url_prefix}/me",
            headers={"Authorization": f"bearer {self.access_tokens['primary_user']}"},
            name=f"{self.url_prefix}/me",
        )
        self.loyalty_cards = {}
        self.trusted_loyalty_cards = {}
        self.join_ids = []
        self.payment_cards = {}
        self.trusted_channel_payment_cards = {}


def set_retry_and_timeout(retry_time_value: float, timeout_value: float) -> None:
    global retry_time, timeout  # noqa: PLW0603

    retry_time = retry_time_value
    timeout = timeout_value
