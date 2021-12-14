import random
from enum import IntEnum, auto

from locust import HttpUser, SequentialTaskSet, constant, task
from locust.exception import StopUser

from data_population.fixtures.client import CLIENT_ONE, NON_RESTRICTED_CLIENTS
from locust_config import AUTOLINK, MEMBERSHIP_PLANS, check_suite_whitelist, repeat_task
from request_data import membership_card, payment_card, service
from request_data.hermes import post_scheme_account_status
from vault import load_secrets


class MembershipCardJourney(IntEnum):
    ADD = auto()
    ENROL = auto()
    REGISTER = auto()


class UserBehavior(SequentialTaskSet):
    def __init__(self, parent):
        self.consent = {}
        self.single_prop_header = {}
        self.membership_plan_total = MEMBERSHIP_PLANS
        self.payment_cards = []
        self.membership_cards = []
        self.service_counter = 0
        self.client_secrets = load_secrets()
        self.url_prefix = "/ubiquity"
        self.pub_key = self.client_secrets[CLIENT_ONE["bundle_id"]]["public_key"]
        super(UserBehavior, self).__init__(parent)

    @task
    def setup_headers(self):
        if not self.pub_key:
            self.client_secrets = load_secrets()
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
    def post_service(self):
        self.service_counter += 1
        self.client.post(
            f"{self.url_prefix}/service", json=self.consent, headers=self.single_prop_header, name="LC001 - Register customer with Bink"
        )

    @check_suite_whitelist
    @task
    @repeat_task(20)
    # LC002 - Retrieve loyalty plans
    def get_membership_plans(self):
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
    def post_payment_cards_single_property(self):
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

    def post_membership_card_add_auth(self, plan_id):
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

    def post_membership_cards_enrol(self, plan_id):
        enrol_json = membership_card.random_join_json(plan_id, self.pub_key)
        resp = self.client.post(
            f"{self.url_prefix}/membership_cards", json=enrol_json, headers=self.single_prop_header, name="LC005 - Register loyalty card"
        )

        mcard = {
            "id": resp.json()["id"],
        }
        self.membership_cards.append(mcard)

    def post_and_patch_membership_cards_register(self, plan_id):
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

        post_scheme_account_status(membership_card.PRE_REGISTERED_CARD_STATUS, mcard_id)
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
    def post_membership_cards(self):
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
    def get_membership_cards(self):
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
    def delete_membership_card(self):
        check_counter = self.service_counter - 1
        if check_counter % 5 == 0:
            mcard = self.membership_cards[0]
            self.client.delete(
                f"{self.url_prefix}/membership_card/{mcard['id']}", headers=self.single_prop_header, name="LC006 - Delete loyalty card"
            )

    @check_suite_whitelist
    @task
    def stop_locust_after_test_suite(self):
        raise StopUser()


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = constant(0)
