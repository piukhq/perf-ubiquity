import random
from typing import TYPE_CHECKING, Any

from locust import HttpUser, SequentialTaskSet, constant, task

from ubiquity_performance_test.data_population.fixtures.client import CLIENT_ONE, NON_RESTRICTED_CLIENTS
from ubiquity_performance_test.locust_config import AUTOLINK, MEMBERSHIP_PLANS, repeat_task
from ubiquity_performance_test.request_data import membership_card, payment_card, service
from ubiquity_performance_test.vault import vault_secrets

if TYPE_CHECKING:
    from ubiquity_performance_test.request_data.service import ConsentType


class UserBehavior(SequentialTaskSet):
    def __init__(self, parent: type[SequentialTaskSet]) -> None:
        self.consent: "ConsentType" = {}
        self.single_prop_header: dict = {}
        self.membership_plan_total = MEMBERSHIP_PLANS
        self.payment_cards: list = []
        self.membership_cards: list = []
        self.service_counter = 0
        self.client_secrets = vault_secrets.channel_info["channel_secrets"]
        self.url_prefix = "/ubiquity"
        self.pub_key = self.client_secrets[CLIENT_ONE["bundle_id"]]["public_key"]
        self.mcard_params: dict[str, Any] = {
            "fields": [
                "id",
                "membership_plan",
                "status",
                "payment_cards",
                "card",
                "account",
                "balances",
                "images",
                "voucher",
            ],
        }
        super().__init__(parent)

    @task
    def setup_headers(self) -> None:
        if not self.pub_key:
            self.client_secrets = vault_secrets.channel_info
            self.pub_key = self.client_secrets[CLIENT_ONE["bundle_id"]]["public_key"]

        self.payment_cards = []
        self.membership_cards = []
        self.consent = service.generate_random()
        email = self.consent["consent"]["email"]
        timestamp = self.consent["consent"]["timestamp"]

        user_client = random.choice(NON_RESTRICTED_CLIENTS)
        single_prop_jwt_secret = self.client_secrets[user_client["bundle_id"]]["jwt_secret"]
        self.single_prop_header = service.generate_auth_header(email, timestamp, user_client, single_prop_jwt_secret)

    @task
    # LC001 - Register customer with Bink
    def post_service(self) -> None:
        self.service_counter += 1
        self.client.post(
            f"{self.url_prefix}/service",
            json=self.consent,
            headers=self.single_prop_header,
            name="LC001 - Register customer with Bink",
        )

    @task
    @repeat_task(20)
    # LC002 - Retrieve loyalty plans
    def get_membership_plans(self) -> None:
        plan_filters = {
            "fields": ["id", "status", "feature_set", "account", "images", "balances", "card", "content"],
        }
        resp = self.client.get(
            f"{self.url_prefix}/membership_plans",
            params=plan_filters,
            headers=self.single_prop_header,
            name="LC002 - Retrieve loyalty plans",
        )

        self.membership_plan_total = len(resp.json())

    @task
    @repeat_task(2)
    # LC003 - Register payment cards with BINK
    def post_payment_cards_2(self) -> None:
        pcard = payment_card.generate_unencrypted_random()
        pcard_json = payment_card.encrypt(pcard, self.pub_key)
        resp = self.client.post(
            f"{self.url_prefix}/payment_cards",
            json=pcard_json,
            headers=self.single_prop_header,
            name="LC003 - Register payment cards with BINK",
        )

        pcard_id = resp.json()["id"]
        pcard = {"id": pcard_id, "json": pcard_json}
        self.payment_cards.append(pcard)

    @task
    @repeat_task(20)
    def get_payment_cards_2_no_thread(self) -> None:
        self.client.get(
            f"{self.url_prefix}/payment_cards",
            headers=self.single_prop_header,
            params={"threading_threshold": 20},
            name="/payment_cards 2 no thread",
        )

    @task
    @repeat_task(20)
    def get_payment_cards_2(self) -> None:
        self.client.get(
            f"{self.url_prefix}/payment_cards",
            headers=self.single_prop_header,
            params={"threading_threshold": 1},
            name="/payment_cards 2 yes thread",
        )

    @task
    # LC003 - Register payment cards with BINK
    def post_payment_cards_3(self) -> None:
        pcard = payment_card.generate_unencrypted_random()
        pcard_json = payment_card.encrypt(pcard, self.pub_key)
        resp = self.client.post(
            f"{self.url_prefix}/payment_cards",
            json=pcard_json,
            headers=self.single_prop_header,
            name="LC003 - Register payment cards with BINK",
        )

        pcard_id = resp.json()["id"]
        pcard = {"id": pcard_id, "json": pcard_json}
        self.payment_cards.append(pcard)

    @task
    @repeat_task(20)
    def get_payment_cards_3_no_thread(self) -> None:
        self.client.get(
            f"{self.url_prefix}/payment_cards",
            headers=self.single_prop_header,
            params={"threading_threshold": 20},
            name="/payment_cards 3 no thread",
        )

    @task
    @repeat_task(20)
    def get_payment_cards_3(self) -> None:
        self.client.get(
            f"{self.url_prefix}/payment_cards",
            headers=self.single_prop_header,
            params={"threading_threshold": 1},
            name="/payment_cards 3 yes thread",
        )

    @task
    # LC003 - Register payment cards with BINK
    def post_payment_cards_4(self) -> None:
        pcard = payment_card.generate_unencrypted_random()
        pcard_json = payment_card.encrypt(pcard, self.pub_key)
        resp = self.client.post(
            f"{self.url_prefix}/payment_cards",
            json=pcard_json,
            headers=self.single_prop_header,
            name="LC003 - Register payment cards with BINK",
        )

        pcard_id = resp.json()["id"]
        pcard = {"id": pcard_id, "json": pcard_json}
        self.payment_cards.append(pcard)

    @task
    @repeat_task(20)
    def get_payment_cards_4_no_thread(self) -> None:
        self.client.get(
            f"{self.url_prefix}/payment_cards",
            headers=self.single_prop_header,
            params={"threading_threshold": 20},
            name="/payment_cards 4 no thread",
        )

    @task
    @repeat_task(20)
    def get_payment_cards_4(self) -> None:
        self.client.get(
            f"{self.url_prefix}/payment_cards",
            headers=self.single_prop_header,
            params={"threading_threshold": 1},
            name="/payment_cards 4 yes thread",
        )

    @task
    @repeat_task(2)
    # LC004 - Register loyalty card
    def post_membership_cards_2(self) -> None:
        plan_id = random.choice(range(1, self.membership_plan_total + 1))
        add_json = membership_card.random_add_json(plan_id, self.pub_key)
        resp = self.client.post(
            f"{self.url_prefix}/membership_cards",
            params=AUTOLINK,
            json=add_json,
            headers=self.single_prop_header,
            name="LC004 - Register loyalty card",
        )
        mcard = {
            "id": resp.json()["id"],
        }
        self.membership_cards.append(mcard)

    @task
    @repeat_task(20)
    # LC004 - Retrieve linked loyalty cards
    def get_membership_cards_2_no_thread(self) -> None:
        self.mcard_params["threading_threshold"] = 20
        self.client.get(
            f"{self.url_prefix}/membership_cards",
            params=self.mcard_params,
            headers=self.single_prop_header,
            name="/membership_cards 2 no thread",
        )

    @task
    @repeat_task(20)
    # LC004 - Retrieve linked loyalty cards
    def get_membership_cards_2(self) -> None:
        self.mcard_params["threading_threshold"] = 1
        self.client.get(
            f"{self.url_prefix}/membership_cards",
            params=self.mcard_params,
            headers=self.single_prop_header,
            name="/membership_cards 2 yes thread",
        )

    @task
    # LC004 - Register loyalty card
    def post_membership_cards_3(self) -> None:
        plan_id = random.choice(range(1, self.membership_plan_total + 1))
        add_json = membership_card.random_add_json(plan_id, self.pub_key)
        resp = self.client.post(
            f"{self.url_prefix}/membership_cards",
            params=AUTOLINK,
            json=add_json,
            headers=self.single_prop_header,
            name="LC004 - Register loyalty card",
        )
        mcard = {
            "id": resp.json()["id"],
        }
        self.membership_cards.append(mcard)

    @task
    @repeat_task(20)
    # LC004 - Retrieve linked loyalty cards
    def get_membership_cards_3_no_thread(self) -> None:
        self.mcard_params["threading_threshold"] = 20
        self.client.get(
            f"{self.url_prefix}/membership_cards",
            params=self.mcard_params,
            headers=self.single_prop_header,
            name="/membership_cards 3 no thread",
        )

    @task
    @repeat_task(20)
    # LC004 - Retrieve linked loyalty cards
    def get_membership_cards_3(self) -> None:
        self.mcard_params["threading_threshold"] = 1
        self.client.get(
            f"{self.url_prefix}/membership_cards",
            params=self.mcard_params,
            headers=self.single_prop_header,
            name="/membership_cards 3 yes thread",
        )

    @task
    # LC004 - Register loyalty card
    def post_membership_cards_4(self) -> None:
        plan_id = random.choice(range(1, self.membership_plan_total + 1))
        add_json = membership_card.random_add_json(plan_id, self.pub_key)
        resp = self.client.post(
            f"{self.url_prefix}/membership_cards",
            params=AUTOLINK,
            json=add_json,
            headers=self.single_prop_header,
            name="LC004 - Register loyalty card",
        )
        mcard = {
            "id": resp.json()["id"],
        }
        self.membership_cards.append(mcard)

    @task
    @repeat_task(20)
    # LC004 - Retrieve linked loyalty cards
    def get_membership_cards_4_no_thread(self) -> None:
        self.mcard_params["threading_threshold"] = 20
        self.client.get(
            f"{self.url_prefix}/membership_cards",
            params=self.mcard_params,
            headers=self.single_prop_header,
            name="/membership_cards 4 no thread",
        )

    @task
    @repeat_task(20)
    # LC004 - Retrieve linked loyalty cards
    def get_membership_cards_4(self) -> None:
        self.mcard_params["threading_threshold"] = 1
        self.client.get(
            f"{self.url_prefix}/membership_cards",
            params=self.mcard_params,
            headers=self.single_prop_header,
            name="/membership_cards 4 yes thread",
        )


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]  # noqa: RUF012
    wait_time = constant(0)
