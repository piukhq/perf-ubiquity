import random
from enum import IntEnum, auto
from typing import TYPE_CHECKING

from locust import HttpUser, SequentialTaskSet, constant, task
from locust.exception import StopUser

from ubiquity_performance_test.data_population.fixtures.client import CLIENT_ONE, NON_RESTRICTED_CLIENTS
from ubiquity_performance_test.locust_angelia.database.jobs import set_status_for_loyalty_card
from ubiquity_performance_test.locust_config import AUTOLINK, MEMBERSHIP_PLANS, check_suite_whitelist, repeat_task
from ubiquity_performance_test.request_data import membership_card, payment_card, service
from ubiquity_performance_test.vault import vault_secrets

if TYPE_CHECKING:
    from ubiquity_performance_test.request_data.service import ConsentType


class MembershipCardJourney(IntEnum):
    ADD = auto()
    ENROL = auto()
    REGISTER = auto()


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

    @check_suite_whitelist
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

    @check_suite_whitelist
    @task
    # LC003 - Register payment cards with BINK
    def post_payment_cards_single_property(self) -> None:
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

    def post_membership_card_add_auth(self, plan_id: int) -> None:
        add_json = membership_card.random_add_json(plan_id, self.pub_key)
        resp = self.client.post(
            f"{self.url_prefix}/membership_cards",
            params=AUTOLINK,
            json=add_json,
            headers=self.single_prop_header,
            name="LC005 - Register loyalty card",
        )
        mcard = {
            "id": resp.json()["id"],
        }
        self.membership_cards.append(mcard)

    def post_membership_cards_enrol(self, plan_id: int) -> None:
        enrol_json = membership_card.random_join_json(plan_id, self.pub_key)
        resp = self.client.post(
            f"{self.url_prefix}/membership_cards",
            json=enrol_json,
            headers=self.single_prop_header,
            name="LC005 - Register loyalty card",
        )

        mcard = {
            "id": resp.json()["id"],
        }
        self.membership_cards.append(mcard)

    def post_and_patch_membership_cards_register(self, plan_id: int) -> None:
        ghost_card_add_json = membership_card.random_add_ghost_card_json(plan_id, self.pub_key)
        resp = self.client.post(
            f"{self.url_prefix}/membership_cards",
            params=AUTOLINK,
            json=ghost_card_add_json,
            headers=self.single_prop_header,
            name="LC005 - Register loyalty card",
        )

        mcard_id = resp.json()["id"]
        mcard = {
            "id": mcard_id,
        }
        self.membership_cards.append(mcard)

        set_status_for_loyalty_card(mcard_id, membership_card.PRE_REGISTERED_CARD_STATUS)
        register_json = membership_card.random_registration_json(self.pub_key)
        self.client.patch(
            f"{self.url_prefix}/membership_card/{mcard_id}",
            json=register_json,
            headers=self.single_prop_header,
            name="LC005 - Register loyalty card",
        )

    @check_suite_whitelist
    @task
    # LC005 - Register loyalty card
    def post_membership_cards(self) -> None:
        plan_id = random.choice(range(1, self.membership_plan_total + 1))
        journey = random.choice(list(MembershipCardJourney))

        if journey == MembershipCardJourney.ADD:
            self.post_membership_card_add_auth(plan_id)
        elif journey == MembershipCardJourney.ENROL:
            self.post_membership_cards_enrol(plan_id)
        elif journey == MembershipCardJourney.REGISTER:
            self.post_and_patch_membership_cards_register(plan_id)
        else:
            raise RuntimeError(
                f"Invalid journey: {journey}, passed into to POST membership card test, "
                f"available journeys: {list(MembershipCardJourney)}"
            )

    @check_suite_whitelist
    @task
    @repeat_task(20)
    # LC004 - Retrieve linked loyalty cards
    def get_membership_cards(self) -> None:
        mcard_filters = {
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
        self.client.get(
            f"{self.url_prefix}/membership_cards",
            params=mcard_filters,
            headers=self.single_prop_header,
            name="LC004 - Retrieve linked loyalty cards",
        )

    @check_suite_whitelist
    @task
    # LC006 - Delete loyalty card
    def delete_membership_card(self) -> None:
        check_counter = self.service_counter - 1
        if check_counter % 5 == 0:
            mcard = self.membership_cards[0]
            self.client.delete(
                f"{self.url_prefix}/membership_card/{mcard['id']}",
                headers=self.single_prop_header,
                name="LC006 - Delete loyalty card",
            )

    @check_suite_whitelist
    @task
    def stop_locust_after_test_suite(self) -> None:
        raise StopUser()


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]  # noqa: RUF012
    wait_time = constant(0)
