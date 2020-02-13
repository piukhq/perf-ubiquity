import random
from enum import Enum

from locust import HttpLocust, TaskSequence, seq_task, constant, task
from requests import codes
from shared_config_storage.vault import secrets

from data_population.fixtures import CLIENT_ONE, CLIENT_TWO, CLIENT_RESTRICTED, MEMBERSHIP_PLAN_IDS
from request_data import service, membership_card, payment_card
from settings import CHANNEL_VAULT_PATH, VAULT_URL, VAULT_TOKEN


class LocustLabel(str, Enum):
    SINGLE_PROPERTY = "- Single property"
    MULTI_PROPERTY = "- Multi property"
    RESTRICTED_PROPERTY = "- Restricted property"


class UserBehavior(TaskSequence):
    def __init__(self, parent):
        self.consent = {}
        self.single_prop_header = {}
        self.multi_prop_header = {}
        self.restricted_prop_header = {}
        self.non_restricted_auth_headers = {}
        self.all_auth_headers = []
        self.payment_cards = []
        self.membership_cards = []
        self.put_counter = 0
        self.service_counter = 0
        channel_info = secrets.read_vault(CHANNEL_VAULT_PATH, VAULT_URL, VAULT_TOKEN)
        self.client_secrets = {client: secret["jwt_secret"] for client, secret in channel_info.items()}
        super(UserBehavior, self).__init__(parent)

    @seq_task(1)
    def test_setup(self):
        self.payment_cards = []
        self.membership_cards = []
        self.consent = service.generate_random()
        email = self.consent["consent"]["email"]
        timestamp = self.consent["consent"]["timestamp"]
        self.single_prop_header = service.generate_auth_header(email, timestamp, CLIENT_ONE)
        self.multi_prop_header = service.generate_auth_header(email, timestamp, CLIENT_TWO)
        self.restricted_prop_header = service.generate_auth_header(email, timestamp, CLIENT_RESTRICTED)
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

    @seq_task(3)
    def get_service(self):
        for auth_header in self.all_auth_headers:
            self.client.get("/service", headers=auth_header, name=f"/service {LocustLabel.SINGLE_PROPERTY}")

    @seq_task(4)
    def get_membership_plans(self):
        for locust_label, auth_header in self.non_restricted_auth_headers.items():
            self.client.get("/membership_plans", headers=auth_header,
                            name=f"/membership_plans {LocustLabel.SINGLE_PROPERTY}")

    @seq_task(5)
    def get_membership_plans_restricted(self):
        self.client.get("/membership_plans", headers=self.restricted_prop_header,
                        name=f"/membership_plans {LocustLabel.RESTRICTED_PROPERTY}")

    @seq_task(6)
    def get_membership_plan_id(self):
        plan_id = random.choice(MEMBERSHIP_PLAN_IDS)
        for auth_header in self.non_restricted_auth_headers.values():
            self.client.get(f"/membership_plan/{plan_id}", headers=auth_header,
                            name=f"/membership_plan/<plan_id> {LocustLabel.SINGLE_PROPERTY}")

    @seq_task(7)
    def get_membership_plan_id_restricted(self):
        plan_id = random.choice(MEMBERSHIP_PLAN_IDS)
        with self.client.get(f"/membership_plan/{plan_id}", headers=self.restricted_prop_header,
                             name=f"/membership_plan/<plan_id> {LocustLabel.RESTRICTED_PROPERTY}",
                             catch_response=True) as response:
            if response.status_code == codes.NOT_FOUND:
                response.success()

    @seq_task(8)
    @task(2)
    def post_payment_cards(self):
        pcard_json = payment_card.generate_random()
        resp = self.client.post("/payment_cards", json=pcard_json, headers=self.single_prop_header,
                                name=f"/payment_cards {LocustLabel.SINGLE_PROPERTY}")
        pcard_id = resp.json()["id"]
        self.payment_cards.append(pcard_id)

        self.client.post("/payment_cards", json=pcard_json, headers=self.multi_prop_header,
                         name=f"/payment_cards {LocustLabel.MULTI_PROPERTY}")

    @seq_task(9)
    @task(7)
    def post_membership_cards_add(self):
        plan_id = random.choice(MEMBERSHIP_PLAN_IDS)
        mcard_json = membership_card.random_add_json(plan_id)
        resp = self.client.post("/membership_cards", json=mcard_json, headers=self.single_prop_header,
                                name=f"/membership_cards {LocustLabel.SINGLE_PROPERTY}")

        mcard = {
            'id': resp.json()['id'],
            'plan_id': plan_id
        }
        self.membership_cards.append(mcard)

        self.client.post("/membership_cards", json=mcard_json, headers=self.multi_prop_header,
                         name=f"/membership_cards {LocustLabel.MULTI_PROPERTY}")

    @seq_task(10)
    @task(7)
    def post_membership_cards_add_restricted(self):
        mcard_json = membership_card.random_add_json(MEMBERSHIP_PLAN_IDS)
        with self.client.get("/membership_cards", json=mcard_json, headers=self.restricted_prop_header,
                             name=f"/membership_cards {LocustLabel.RESTRICTED_PROPERTY}",
                             catch_response=True) as response:
            if response.status_code == codes.BAD_REQUEST:
                response.success()

    @seq_task(11)
    def post_membership_cards_join(self):
        plan_id = random.choice(MEMBERSHIP_PLAN_IDS)
        mcard_json = membership_card.random_join_json(MEMBERSHIP_PLAN_IDS)
        resp = self.client.post("/membership_cards", json=mcard_json, headers=self.single_prop_header,
                                name=f"/membership_cards {LocustLabel.SINGLE_PROPERTY}")

        mcard = {
            'id': resp.json()['id'],
            'plan_id': plan_id
        }
        self.membership_cards.append(mcard)

        self.client.post("/membership_cards", json=mcard_json, headers=self.multi_prop_header,
                         name=f"/membership_cards {LocustLabel.MULTI_PROPERTY}")

    @seq_task(12)
    def post_membership_cards_join_restricted(self):
        mcard_json = membership_card.random_join_json(MEMBERSHIP_PLAN_IDS)
        with self.client.get("/membership_cards", json=mcard_json, headers=self.restricted_prop_header,
                             name=f"/membership_cards {LocustLabel.RESTRICTED_PROPERTY}",
                             catch_response=True) as response:
            if response.status_code == codes.BAD_REQUEST:
                response.success()

    @seq_task(8)
    def patch_payment_card_id_membership_card_id(self):
        pcard_id = self.payment_cards[0]
        mcard_id = self.membership_cards[0]
        for auth_header in self.non_restricted_auth_headers.values():
            self.client.patch(f"/payment_card/{pcard_id}/membership_card/{mcard_id}", headers=auth_header,
                              name=f"/payment_card/<pcard_id>/membership_card/<mcard_id> "
                                   f"{LocustLabel.SINGLE_PROPERTY}")

    @seq_task(8)
    def patch_payment_card_id_membership_card_id_restricted(self):
        pcard_id = self.payment_cards[0]
        mcard_id = self.membership_cards[0]
        with self.client.patch(f"/payment_card/{pcard_id}/membership_card/{mcard_id}",
                               headers=self.restricted_prop_header, catch_response=True,
                               name=f"/payment_card/<pcard_id>/membership_card/<mcard_id> "
                                    f"{LocustLabel.RESTRICTED_PROPERTY}") as response:
            if response.status_code == codes.FORBIDDEN:
                response.success()

    @seq_task(9)
    def patch_membership_card_id_payment_card_id(self):
        mcard_id = self.membership_cards[1]
        pcard_id = self.payment_cards[1]
        for label, auth_header in self.non_restricted_auth_headers.items():
            self.client.patch(f"/membership_card/{mcard_id}/payment_card/{pcard_id}", headers=auth_header,
                              name=f"/membership_card/<mcard_id>/payment_card/<pcard_id> "
                                   f"{LocustLabel.SINGLE_PROPERTY}")

    @seq_task(8)
    def patch_membership_card_id_payment_card_id_restricted(self):
        mcard_id = self.membership_cards[1]
        pcard_id = self.payment_cards[1]
        with self.client.patch(f"/membership_card/{mcard_id}/payment_card/{pcard_id}",
                               headers=self.restricted_prop_header, catch_response=True,
                               name=f"/membership_card/<mcard_id>/payment_card/<pcard_id> "
                                    f"{LocustLabel.RESTRICTED_PROPERTY}") as response:
            if response.status_code == codes.FORBIDDEN:
                response.success()

    @seq_task(10)
    def put_membership_card(self):
        self.put_counter += 1
        if self.put_counter % 4 == 0:
            mcard_id = self.membership_cards[0]['id']
            plan_id = self.membership_cards[0]['membership_plan_id']
            put_json = membership_card.random_add_json(plan_id)

            self.client.put(f"/membership_card/{mcard_id}", json=put_json, headers=self.single_prop_header,
                            name=f"/membership_card/<card_id> {LocustLabel.SINGLE_PROPERTY}")

            mcard_id = self.membership_cards[1]
            self.client.put(f"/membership_card/{mcard_id}", json=put_json, headers=self.multi_prop_header,
                            name=f"/membership_card/<card_id> {LocustLabel.MULTI_PROPERTY}")

    @seq_task(11)
    def patch_membership_cards_id_add(self):
        mcard_id = self.membership_cards[1]
        mcard_json = membership_card.random_patch_json()
        self.client.patch(f"/membership_card/{mcard_id}", json=mcard_json, headers=self.single_prop_header,
                          name=f"/membership_card/<mcard_id> {LocustLabel.SINGLE_PROPERTY}")

        mcard_id = self.membership_cards[2]
        self.client.patch(f"/membership_card/{mcard_id}", json=mcard_json, headers=self.multi_prop_header,
                          name=f"/membership_card/<mcard_id> {LocustLabel.MULTI_PROPERTY}")

        # mcard_id = self.membership_cards[3]
        # with self.client.patch(f"/membership_card/{mcard_id}", json=mcard_json, headers=self.restricted_prop_header,
        #                        name=f"/membership_card/<mcard_id> {LocustLabel.RESTRICTED_PROPERTY}",
        #                        catch_response=True) as response:
        #     if response.status_code == codes.NOT_FOUND:
        #         response.success()

    @seq_task(12)
    def patch_membership_cards_id_ghost(self):
        task_counter = 2
        for x in range(0, task_counter):
            # reset index if range > max number of membership cards
            converted_index = x % len(self.membership_cards)
            mcard_id = self.membership_cards[converted_index]
            mcard_json = membership_card.random_registration_json()
            self.client.patch(f"/membership_card/{mcard_id}", json=mcard_json, headers=self.single_prop_header,
                              name=f"/membership_card/<mcard_id> {LocustLabel.SINGLE_PROPERTY}")

            converted_index = x % len(self.membership_cards) + task_counter
            mcard_id = self.membership_cards[converted_index]
            self.client.patch(f"/membership_card/{mcard_id}", json=mcard_json, headers=self.multi_prop_header,
                              name=f"/membership_card/<mcard_id> {LocustLabel.MULTI_PROPERTY}")

    @seq_task(13)
    def get_payment_cards(self):
        for auth_header in self.non_restricted_auth_headers.values():
            self.client.get("/payment_cards", headers=auth_header,
                            name=f"/payment_cards {LocustLabel.SINGLE_PROPERTY}")

        self.client.get("/payment_cards", headers=self.restricted_prop_header,
                        name=f"/payment_cards {LocustLabel.RESTRICTED_PROPERTY}")

    @seq_task(13)
    def get_payment_card(self):
        for payment_card_id in self.payment_cards:
            for auth_header in self.non_restricted_auth_headers.values():
                self.client.get(f"/payment_card/{payment_card_id}", headers=auth_header,
                                name=f"/payment_card/<pcard_id> {LocustLabel.SINGLE_PROPERTY}")

        payment_card_id = self.payment_cards[0]
        with self.client.get(f"/payment_card/{payment_card_id}", headers=self.restricted_prop_header,
                             name=f"/payment_card/<pcard_id> {LocustLabel.RESTRICTED_PROPERTY}",
                             catch_response=True) as response:
            if response.status_code == codes.NOT_FOUND:
                response.success()

    @seq_task(14)
    def get_membership_cards(self):
        for auth_header in self.non_restricted_auth_headers.values():
            self.client.get("/membership_cards", headers=auth_header,
                            name=f"/membership_cards {LocustLabel.SINGLE_PROPERTY}")

        self.client.get("/membership_cards", headers=self.restricted_prop_header,
                        name=f"/membership_cards {LocustLabel.RESTRICTED_PROPERTY}")

    @seq_task(16)
    def get_membership_card(self):
        task_counter = 8
        for x in range(0, task_counter):
            # reset index if range > max number of membership cards
            converted_index = x % len(self.membership_cards)
            mcard_id = self.membership_cards[converted_index]
            for label, auth_header in self.non_restricted_auth_headers.items():
                self.client.get(f"/membership_card/{mcard_id}", headers=auth_header,
                                name=f"/membership_card/<card_id> {label}")

    @seq_task(17)
    def delete_payment_card(self):
        for pcard_id in self.payment_cards:
            for label, auth_header in self.non_restricted_auth_headers.items():
                self.client.delete(f"/payment_card/{pcard_id}", headers=auth_header,
                                   name=f"/payment_card/<card_id> {label}")

    @seq_task(18)
    def delete_membership_card(self):
        for mcard in self.membership_cards:
            for label, auth_header in self.non_restricted_auth_headers.items():
                self.client.delete(f"/membership_card/{mcard['id']}", headers=auth_header,
                                   name=f"/membership_card/<card_id> {label}")

    @seq_task(19)
    def delete_service(self):
        self.service_counter += 1
        if self.service_counter % 10 == 0:
            for auth_header in self.all_auth_headers:
                self.client.delete("/service", headers=auth_header,
                                   name=f"/service {LocustLabel.SINGLE_PROPERTY}")


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    wait_time = constant(0)
