import random

from locust import HttpLocust, TaskSequence, seq_task, constant, task

from request_data import service, membership_card, payment_card, membership_plan
from request_data.membership_plan import PlanIDs


class UserBehavior(TaskSequence):

    def __init__(self, parent):
        super(UserBehavior, self).__init__(parent)
        self.headers = {}
        self.payment_cards = []
        self.membership_cards = []
        self.put_counter = 0

    def setup(self):
        consent = service.generate_static()
        email = consent["consent"]["email"]
        timestamp = consent["consent"]["timestamp"]
        test_headers = service.generate_auth_header(email, timestamp)
        self.client.post("/service", json=consent, headers=test_headers)
        resp = self.client.get("/membership_plans", headers=test_headers)
        membership_plan_ids = [plan["id"] for plan in resp.json()]
        if PlanIDs.TEST_SCHEME_ID not in membership_plan_ids:
            raise ValueError(
                f"No performance test scheme in database (ID: {PlanIDs.TEST_SCHEME_ID}), "
                f"please run data population.."
            )

    def on_start(self):
        self.headers = {}
        self.payment_cards = []
        self.membership_cards = []

    @seq_task(1)
    def post_service(self):
        consent = service.generate_random()
        email = consent["consent"]["email"]
        timestamp = consent["consent"]["timestamp"]
        self.headers = service.generate_auth_header(email, timestamp)
        self.client.post("/service", json=consent, headers=self.headers)

    @seq_task(2)
    def get_service(self):
        self.client.get("/service", headers=self.headers)

    @seq_task(3)
    def get_membership_plans(self):
        self.client.get("/membership_plans", headers=self.headers)

    @seq_task(4)
    def get_membership_plan_id(self):
        plan_id = random.choice(list(membership_plan.PlanIDs))
        self.client.get(f"/membership_plan/{plan_id}", headers=self.headers, name="/membership_plan/{plan_id}")

    @seq_task(5)
    @task(2)
    def post_payment_cards(self):
        pcard_json = payment_card.generate_random()
        resp = self.client.post("/payment_cards", json=pcard_json, headers=self.headers)
        pcard_id = resp.json()['id']
        self.payment_cards.append(pcard_id)

    @seq_task(6)
    @task(8)
    def post_membership_cards_add(self):
        mcard_json = membership_card.random_add_json()
        resp = self.client.post("/membership_cards", json=mcard_json, headers=self.headers)
        mcard_id = resp.json()['id']
        self.membership_cards.append(mcard_id)

    @seq_task(7)
    def post_membership_cards_join(self):
        mcard_json = membership_card.random_join_json()
        resp = self.client.post("/membership_cards", json=mcard_json, headers=self.headers)
        mcard_id = resp.json()['id']
        self.membership_cards.append(mcard_id)

    @seq_task(8)
    def patch_payment_card_id_membership_card_id(self):
        pcard_id = self.payment_cards[0]
        mcard_id = self.membership_cards[0]
        self.client.patch(f"/payment_card/{pcard_id}/membership_card/{mcard_id}", headers=self.headers,
                          name="/payment_card/{pcard_id}/membership_card/{mcard_id}")

    @seq_task(9)
    def patch_membership_card_id_payment_card_id(self):
        mcard_id = self.membership_cards[1]
        pcard_id = self.payment_cards[1]
        self.client.patch(f"/membership_card/{mcard_id}/payment_card/{pcard_id}", headers=self.headers,
                          name="/membership_card/{mcard_id}/payment_card/{pcard_id}")

    @seq_task(10)
    def put_membership_card(self):
        self.put_counter += 1
        # remove me after we test this once
        print(self.put_counter)
        if self.put_counter % 4 == 0:
            mcard_id = self.membership_cards[0]
            mcard_json = membership_card.random_add_json()
            self.client.put(f"/membership_card/{mcard_id}", json=mcard_json, headers=self.headers,
                            name="/membership_card/{mcard_id}")

    @seq_task(11)
    def patch_membership_cards_id_add(self):
        mcard_id = self.membership_cards[1]
        mcard_json = membership_card.random_patch_json()
        self.client.patch(f"/membership_card/{mcard_id}", json=mcard_json, headers=self.headers,
                          name="/membership_card/{mcard_id} - ADD")

    @seq_task(12)
    def patch_membership_cards_id_ghost(self):
        task_counter = 2
        for x in range(0, task_counter):
            converted_index = x % len(self.membership_cards)
            mcard_id = self.membership_cards[converted_index]
            mcard_json = membership_card.random_registration_json()
            self.client.patch(f"/membership_card/{mcard_id}", json=mcard_json, headers=self.headers,
                              name="/membership_card/{mcard_id} - GHOST")

    @seq_task(13)
    def get_payment_cards(self):
        self.client.get("/payment_cards", headers=self.headers)

    @seq_task(14)
    def get_membership_cards(self):
        self.client.get("/membership_cards", headers=self.headers)

    @seq_task(15)
    def get_membership_card(self):
        task_counter = 8
        for x in range(0, task_counter):
            converted_index = x % len(self.membership_cards)
            self.client.get(f"/membership_card/{converted_index}", headers=self.headers,
                            name="/membership_card/{mcard_id}")

    @seq_task(16)
    def get_membership_transactions(self):
        self.client.get("/membership_transactions", headers=self.headers)

    @seq_task(17)
    def delete_payment_card(self):
        for pcard_id in self.payment_cards:
            self.client.delete(f"/payment_card/{pcard_id}", headers=self.headers,
                               name="/payment_card/{pcard_id}")

    @seq_task(18)
    def delete_membership_card(self):
        for mcard_id in self.membership_cards:
            self.client.delete(f"/membership_card/{mcard_id}", headers=self.headers,
                               name="/membership_card/{mcard_id}")


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    wait_time = constant(0)
