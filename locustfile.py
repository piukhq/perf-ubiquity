import json
import random
import time
from enum import Enum

from locust import HttpLocust, TaskSequence, seq_task, constant, task
from locust.exception import StopLocust
from requests import codes
from shared_config_storage.vault import secrets

from data_population.create_tsv import MEMBERSHIP_PLANS
from data_population.fixtures.client import CLIENT_ONE, CLIENT_RESTRICTED, NON_RESTRICTED_CLIENTS
from locust_config import check_suite_whitelist
from request_data import service, membership_card, payment_card
from request_data.membership_plan import increment_membership_plan_counter
from request_data.hermes import post_scheme_account_status
from settings import CHANNEL_VAULT_PATH, VAULT_URL, VAULT_TOKEN, LOCAL_SECRETS, LOCAL_SECRETS_PATH

# Change this to specify how many channels the locust tests use
TOTAL_CLIENTS = 6
PCARD_DECRYPT_WAIT_TIME = 120
MULTIPLE_PROPERTY_PCARD_INDEX = 0

AUTOLINK = {"autolink": "true"}


class LocustLabel(str, Enum):
    SINGLE_PROPERTY = "- Single property"
    MULTI_PROPERTY = "- Multi property"
    SINGLE_RESTRICTED_PROPERTY = "- Single restricted property"
    MULTI_RESTRICTED_PROPERTY = "- Multi restricted property"


def load_secrets():
    if LOCAL_SECRETS:
        with open(LOCAL_SECRETS_PATH) as fp:
            channel_info = json.load(fp)
    else:
        channel_info = secrets.read_vault(CHANNEL_VAULT_PATH, VAULT_URL, VAULT_TOKEN)

    return channel_info


class UserBehavior(TaskSequence):
    def __init__(self, parent):
        self.consent = {}
        self.single_prop_header = {}
        self.multi_prop_header = {}
        self.restricted_prop_header = {}
        self.non_restricted_auth_headers = {}
        self.all_auth_headers = []
        self.membership_plan_total = MEMBERSHIP_PLANS
        self.payment_cards = []
        self.membership_cards = []
        self.join_membership_cards = []
        self.put_counter = 0
        self.service_counter = 0
        self.plan_counter = 1
        self.client_secrets = load_secrets()
        self.pub_key = self.client_secrets[CLIENT_ONE['bundle_id']]['public_key']
        super(UserBehavior, self).__init__(parent)

    @seq_task(1)
    def setup_headers(self):
        if not self.pub_key:
            self.client_secrets = load_secrets()
            self.pub_key = self.client_secrets[CLIENT_ONE['bundle_id']]['public_key']

        self.plan_counter = 1
        self.payment_cards = []
        self.membership_cards = []
        self.join_membership_cards = []
        self.consent = service.generate_random()
        email = self.consent["consent"]["email"]
        timestamp = self.consent["consent"]["timestamp"]

        single_prop_jwt_secret = self.client_secrets[CLIENT_ONE['bundle_id']]['jwt_secret']
        self.single_prop_header = service.generate_auth_header(email, timestamp, CLIENT_ONE, single_prop_jwt_secret)
        multi_prop_channel = random.choice(NON_RESTRICTED_CLIENTS[1:TOTAL_CLIENTS - 1])
        multi_prop_jwt_secret = self.client_secrets[multi_prop_channel['bundle_id']]['jwt_secret']
        self.multi_prop_header = service.generate_auth_header(email, timestamp, multi_prop_channel,
                                                              multi_prop_jwt_secret)

        restricted_jwt_secret = self.client_secrets[CLIENT_RESTRICTED['bundle_id']]['jwt_secret']
        self.restricted_prop_header = service.generate_auth_header(email, timestamp, CLIENT_RESTRICTED,
                                                                   restricted_jwt_secret)
        self.non_restricted_auth_headers = {
            LocustLabel.SINGLE_PROPERTY: self.single_prop_header,
            LocustLabel.MULTI_PROPERTY: self.multi_prop_header
        }
        self.all_auth_headers = [self.single_prop_header, self.multi_prop_header, self.restricted_prop_header]

    @seq_task(2)
    def post_service(self):
        for auth_header in self.all_auth_headers:
            self.client.post("/service", json=self.consent, headers=auth_header,
                             name=f"/service {LocustLabel.SINGLE_PROPERTY}")

    @check_suite_whitelist
    @seq_task(3)
    @task(2)
    def get_service(self):
        for auth_header in self.all_auth_headers:
            self.client.get("/service", headers=auth_header, name=f"/service {LocustLabel.SINGLE_PROPERTY}")

    @check_suite_whitelist
    @seq_task(4)
    @task(6)
    def get_membership_plans(self):
        plan_filters = {
            "fields": ["id", "status", "feature_set", "account", "images", "balances", "card", "content"],
        }
        resp = self.client.get("/membership_plans", params=plan_filters, headers=self.single_prop_header,
                               name=f"/membership_plans {LocustLabel.SINGLE_PROPERTY}")

        self.membership_plan_total = len(resp.json())

    @check_suite_whitelist
    @seq_task(5)
    @task(24)
    def get_membership_plan_id(self):
        plan_id = random.choice(range(1, self.membership_plan_total))
        self.client.get(f"/membership_plan/{plan_id}", headers=self.single_prop_header,
                        name=f"/membership_plan/<plan_id> {LocustLabel.SINGLE_PROPERTY}")

    @check_suite_whitelist
    @seq_task(6)
    @task(5)
    def post_membership_cards_single_property_join(self):
        # plan_id = self.plan_counter

        # remove me when midas performance agents are deployed
        plan_id = 1

        mcard_json = membership_card.random_join_json(plan_id, self.pub_key)
        self.plan_counter = increment_membership_plan_counter(self.plan_counter)

        with self.client.post("/membership_cards", params=AUTOLINK, json=mcard_json,
                              headers=self.restricted_prop_header,
                              name=f"/membership_cards {LocustLabel.SINGLE_RESTRICTED_PROPERTY}",
                              catch_response=True) as response:
            if response.status_code == codes.BAD_REQUEST:
                response.success()

        resp = self.client.post("/membership_cards", json=mcard_json, headers=self.single_prop_header,
                                name=f"/membership_cards {LocustLabel.SINGLE_PROPERTY}")

        mcard = {
            'id': resp.json()['id'],
            'plan_id': plan_id,
            'json': mcard_json
        }
        self.join_membership_cards.append(mcard)

    @check_suite_whitelist
    @seq_task(7)
    @task(5)
    def post_payment_cards_single_property(self):
        pcard = payment_card.generate_unencrypted_random()
        first_six = str(pcard['card']['first_six_digits'])
        pcard_json = payment_card.encrypt(pcard, self.pub_key)
        resp = self.client.post("/payment_cards", params=AUTOLINK, json=pcard_json, headers=self.single_prop_header,
                                name=f"/payment_cards {LocustLabel.SINGLE_PROPERTY}")

        if resp.status_code == codes.BAD_REQUEST:
            raise ValueError(f"HTTP 400 response on post payment card request. "
                             f"response json: {resp.json()}, "
                             f"request json: {pcard_json}")

        pcard_id = resp.json()['id']
        pcard = {
            'id': pcard_id,
            'json': pcard_json
        }
        self.payment_cards.append(pcard)

        # wait until pcard is decrypted for mutli-property tests
        for _ in range(0, PCARD_DECRYPT_WAIT_TIME):
            resp = self.client.get(f"/payment_card/{pcard_id}", headers=self.single_prop_header, name="Setup requests")
            if resp.json()['card']['first_six_digits'] == first_six:
                break
            time.sleep(1)
        else:
            raise RuntimeError("Payment card took longer than expected to decrypt on API response, "
                               "please increase wait time and try again")

    @check_suite_whitelist
    @seq_task(8)
    @task(4)
    def post_membership_cards_single_property_add(self):
        plan_id = self.plan_counter

        # remove me when midas performance agents are deployed
        if plan_id == 1:
            plan_id += 1
            self.plan_counter = increment_membership_plan_counter(self.plan_counter)

        mcard_json = membership_card.random_add_json(plan_id, self.pub_key)
        self.plan_counter = increment_membership_plan_counter(self.plan_counter)
        with self.client.post("/membership_cards", params=AUTOLINK, json=mcard_json,
                              headers=self.restricted_prop_header,
                              name=f"/membership_cards {LocustLabel.SINGLE_RESTRICTED_PROPERTY}",
                              catch_response=True) as response:
            if response.status_code == codes.BAD_REQUEST:
                response.success()

        resp = self.client.post("/membership_cards", params=AUTOLINK, json=mcard_json, headers=self.single_prop_header,
                                name=f"/membership_cards {LocustLabel.SINGLE_PROPERTY}")

        mcard = {
            'id': resp.json()['id'],
            'plan_id': plan_id,
            'json': mcard_json
        }
        self.membership_cards.append(mcard)

    @check_suite_whitelist
    @seq_task(9)
    def post_payment_cards_multiple_property(self):
        pcard_json = self.payment_cards[MULTIPLE_PROPERTY_PCARD_INDEX]['json']
        self.client.post("/payment_cards", params=AUTOLINK, json=pcard_json, headers=self.multi_prop_header,
                         name=f"/payment_cards {LocustLabel.MULTI_PROPERTY}")

    @check_suite_whitelist
    @seq_task(10)
    @task(3)
    def get_membership_card_single_property(self):
        for mcard in self.membership_cards:
            self.client.get(f"/membership_card/{mcard['id']}", headers=self.single_prop_header,
                            name=f"/membership_card/<card_id> {LocustLabel.SINGLE_PROPERTY}")

    @check_suite_whitelist
    @seq_task(11)
    def patch_membership_card_id_payment_card_id_single_property(self):
        pcard_id = self.payment_cards[1]['id']
        mcard_id = self.membership_cards[0]['id']
        self.client.patch(f"/membership_card/{mcard_id}/payment_card/{pcard_id}", headers=self.single_prop_header,
                          name=f"/membership_card/<mcard_id>/payment_card/<pcard_id> "
                               f"{LocustLabel.SINGLE_PROPERTY}")

        with self.client.patch(f"/membership_card/{mcard_id}/payment_card/{pcard_id}",
                               headers=self.restricted_prop_header, catch_response=True,
                               name=f"/membership_card/<mcard_id>/payment_card/<pcard_id> "
                                    f"{LocustLabel.SINGLE_RESTRICTED_PROPERTY}") as response:
            if response.status_code == codes.NOT_FOUND:
                response.success()

    @check_suite_whitelist
    @seq_task(12)
    def patch_payment_card_id_membership_card_id_single_property(self):
        pcard_id = self.payment_cards[1]['id']
        mcard_id = self.membership_cards[1]['id']
        self.client.patch(f"/payment_card/{pcard_id}/membership_card/{mcard_id}", headers=self.single_prop_header,
                          name=f"/payment_card/<pcard_id>/membership_card/<mcard_id> "
                               f"{LocustLabel.SINGLE_PROPERTY}")

        with self.client.patch(f"/payment_card/{pcard_id}/membership_card/{mcard_id}",
                               headers=self.restricted_prop_header, catch_response=True,
                               name=f"/payment_card/<pcard_id>/membership_card/<mcard_id> "
                                    f"{LocustLabel.SINGLE_RESTRICTED_PROPERTY}") as response:
            if response.status_code == codes.NOT_FOUND:
                response.success()

    @check_suite_whitelist
    @seq_task(13)
    def post_membership_cards_multiple_property(self):
        for mcard in self.membership_cards:
            mcard_json = mcard['json']
            with self.client.post("/membership_cards", params=AUTOLINK, json=mcard_json,
                                  headers=self.restricted_prop_header,
                                  name=f"/membership_cards {LocustLabel.MULTI_RESTRICTED_PROPERTY}",
                                  catch_response=True) as response:
                if response.status_code == codes.BAD_REQUEST:
                    response.success()

            self.client.post("/membership_cards", params=AUTOLINK, json=mcard_json, headers=self.multi_prop_header,
                             name=f"/membership_cards {LocustLabel.MULTI_PROPERTY}")

    @check_suite_whitelist
    @seq_task(14)
    def patch_membership_card_id_payment_card_id_multiple_property(self):
        pcard_id = self.payment_cards[MULTIPLE_PROPERTY_PCARD_INDEX]['id']
        mcard_id = self.membership_cards[0]['id']
        self.client.patch(f"/membership_card/{mcard_id}/payment_card/{pcard_id}", headers=self.multi_prop_header,
                          name=f"/membership_card/<mcard_id>/payment_card/<pcard_id> "
                               f"{LocustLabel.MULTI_PROPERTY}")

        with self.client.patch(f"/membership_card/{mcard_id}/payment_card/{pcard_id}",
                               headers=self.restricted_prop_header, catch_response=True,
                               name=f"/membership_card/<mcard_id>/payment_card/<pcard_id> "
                                    f"{LocustLabel.MULTI_RESTRICTED_PROPERTY}") as response:
            if response.status_code == codes.NOT_FOUND:
                response.success()

    @check_suite_whitelist
    @seq_task(15)
    def patch_payment_card_id_membership_card_id_multiple_property(self):
        pcard_id = self.payment_cards[MULTIPLE_PROPERTY_PCARD_INDEX]['id']
        mcard_id = self.membership_cards[1]['id']
        self.client.patch(f"/payment_card/{pcard_id}/membership_card/{mcard_id}", headers=self.multi_prop_header,
                          name=f"/payment_card/<pcard_id>/membership_card/<mcard_id> "
                               f"{LocustLabel.MULTI_PROPERTY}")

        with self.client.patch(f"/payment_card/{pcard_id}/membership_card/{mcard_id}",
                               headers=self.restricted_prop_header, catch_response=True,
                               name=f"/payment_card/<pcard_id>/membership_card/<mcard_id> "
                                    f"{LocustLabel.MULTI_RESTRICTED_PROPERTY}") as response:
            if response.status_code == codes.NOT_FOUND:
                response.success()

    @check_suite_whitelist
    @seq_task(16)
    @task(2)
    def get_membership_card_multiple_property(self):
        for mcard in self.membership_cards:
            self.client.get(f"/membership_card/{mcard['id']}", headers=self.multi_prop_header,
                            name=f"/membership_card/<card_id> {LocustLabel.MULTI_PROPERTY}")

    @check_suite_whitelist
    @seq_task(17)
    def patch_membership_cards_id_add(self):
        task_counter = 3
        for x in range(0, task_counter):
            # reset index if range > max number of membership cards
            converted_index = x % len(self.membership_cards)
            mcard_id = self.membership_cards[converted_index]['id']
            mcard_json = membership_card.random_patch_json(self.pub_key)
            self.client.patch(f"/membership_card/{mcard_id}", json=mcard_json, headers=self.single_prop_header,
                              name=f"/membership_card/<mcard_id> {LocustLabel.SINGLE_PROPERTY}")

    @check_suite_whitelist
    @seq_task(18)
    def patch_membership_cards_id_ghost(self):
        status = membership_card.PRE_REGISTERED_CARD_STATUS
        task_counter = 2
        for x in range(0, task_counter):
            # reset index if range > max number of membership cards
            converted_index = x % len(self.membership_cards)
            mcard_id = self.membership_cards[converted_index]['id']
            mcard_json = membership_card.random_registration_json(self.pub_key)

            post_scheme_account_status(status, mcard_id)
            self.client.patch(f"/membership_card/{mcard_id}", json=mcard_json, headers=self.single_prop_header,
                              name=f"/membership_card/<mcard_id> {LocustLabel.SINGLE_PROPERTY}")

    @check_suite_whitelist
    @seq_task(19)
    @task(27)
    def get_payment_cards(self):
        for auth_header in self.non_restricted_auth_headers.values():
            self.client.get("/payment_cards", headers=auth_header,
                            name=f"/payment_cards {LocustLabel.SINGLE_PROPERTY}")

    @check_suite_whitelist
    @seq_task(20)
    @task(27)
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
                "voucher"
            ],
        }
        for auth_header in self.non_restricted_auth_headers.values():
            self.client.get("/membership_cards", params=mcard_filters, headers=auth_header,
                            name=f"/membership_cards {LocustLabel.SINGLE_PROPERTY}")

    @check_suite_whitelist
    @seq_task(21)
    def delete_payment_card_multiple_property(self):
        pcard_id = self.payment_cards[MULTIPLE_PROPERTY_PCARD_INDEX]['id']
        self.client.delete(f"/payment_card/{pcard_id}", headers=self.multi_prop_header,
                           name=f"/payment_card/<card_id> {LocustLabel.MULTI_PROPERTY}")

    @check_suite_whitelist
    @seq_task(22)
    @task(3)
    def delete_payment_card_single_property(self):
        pcard_id = self.payment_cards.pop()['id']
        self.client.delete(f"/payment_card/{pcard_id}", headers=self.single_prop_header,
                           name=f"/payment_card/<card_id> {LocustLabel.SINGLE_PROPERTY}")

    @check_suite_whitelist
    @seq_task(23)
    @task(2)
    def delete_membership_card(self):
        mcard = self.membership_cards.pop()
        self.client.delete(f"/membership_card/{mcard['id']}", headers=self.multi_prop_header,
                           name=f"/membership_card/<card_id> {LocustLabel.MULTI_PROPERTY}")

        self.client.delete(f"/membership_card/{mcard['id']}", headers=self.single_prop_header,
                           name=f"/membership_card/<card_id> {LocustLabel.SINGLE_PROPERTY}")

    @check_suite_whitelist
    @seq_task(24)
    def delete_service(self):
        if self.service_counter % 10 == 0:
            for auth_header in self.all_auth_headers:
                self.client.delete("/service", headers=auth_header,
                                   name=f"/service {LocustLabel.SINGLE_PROPERTY}")

        self.service_counter += 1

    @check_suite_whitelist
    @seq_task(25)
    def stop_locust_after_test_suite(self):
        raise StopLocust()


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    wait_time = constant(0)
