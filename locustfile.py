import random

from locust import HttpLocust, TaskSequence, seq_task, constant

from request_data import service, membership_card, payment_card, membership_plan
from request_data.membership_plan import PlanIDs

WALLET_SIZE = 3


# total task weight: 5
class UserBehavior(TaskSequence):

    def __init__(self, parent):
        super(UserBehavior, self).__init__(parent)
        self.headers = None
        self.test_number = 0

    def setup(self):
        consent = service.generate_static()
        email = consent["consent"]["email"]
        timestamp = consent["consent"]["timestamp"]
        self.test_headers = service.generate_auth_header(email, timestamp)
        self.client.post("/service", json=consent, headers=self.test_headers)
        resp = self.client.get("/membership_plans", headers=self.test_headers)
        membership_plan_ids = [plan["id"] for plan in resp.json()]
        if PlanIDs.TEST_SCHEME_ID not in membership_plan_ids:
            raise ValueError(f"No performance test scheme in database (ID: {PlanIDs.TEST_SCHEME_ID}), please run data population..")

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
        self.client.get(f"/membership_plan/{plan_id}", headers=self.headers)

    @seq_task(5)
    def post_payment_cards(self):
        pass

    @seq_task(6)
    def post_membership_cards(self):
        pass

    @seq_task(7)
    def patch_payment_cards_id_membership_card_id(self):
        pass

    @seq_task(8)
    def post_membership_plans(self):
        pass

    @seq_task(9)
    def put_membership_card(self):
        pass

    @seq_task(10)
    def patch_membership_cards_id(self):
        pass

    @seq_task(11)
    def get_payment_cards(self):
        self.client.get("/payment_cards", headers=self.headers)

    @seq_task(12)
    def get_membership_cards(self):
        self.client.get("/membership_cards", headers=self.headers)

    @seq_task(13)
    def get_membership_card(self):
        self.client.get("/membership_card", headers=self.headers)

    @seq_task(14)
    def get_membership_transactions(self):
        self.client.get("/membership_transactions", headers=self.headers)

    @seq_task(15)
    def delete_membership_card(self):
        pass

    @seq_task(16)
    def delete_payment_card(self):
        pass

    # 
    # @task(1)
    # def get_service(self):
    #     headers = self.create_user()
    #     self.client.get("/service", headers=headers)
    # 
    # @task(1)
    # def get_membership_plans(self):
    #     self.client.get("/membership_plans", headers=self.test_headers)

    # @task(1)
    # def get_membership_plan(self):
    #     self.client.get(f"/membership_plan/{SCHEME_ID}", headers=self.test_headers, name="/membership_plan/<id>")
    # 
    # @task(1)
    # def populate_wallet_autolink(self):
    #     headers = self.create_user()
    #     params = {"autoLink": "True"}
    #     pcard = payment_card.generate_random()
    #     self.client.post("/payment_cards", json=pcard, headers=headers)
    # 
    #     for _ in range(0, WALLET_SIZE):
    #         mcard = membership_card.generate_random()
    #         self.client.post("/membership_cards", json=mcard, headers=headers, params=params)
    # 
    # @task(1)
    # def populate_wallet_manual(self):
    #     headers = self.create_user()
    #     mcard = membership_card.generate_random()
    #     resp = self.client.post("/membership_cards", json=mcard, headers=headers)
    #     mcard_id = resp.json()["id"]
    # 
    #     pcard = payment_card.generate_random()
    #     resp = self.client.post("/payment_cards", json=pcard, headers=headers)
    #     pcard_id = resp.json()["id"]
    # 
    #     self.client.patch(
    #         f"/membership_card/{mcard_id}/payment_card/{pcard_id}",
    #         headers=headers,
    #         name="/membership_card/<mcard_id>/payment_card/<pcard_id>",
    #     )
    # 
    #     for _ in range(0, WALLET_SIZE):
    #         mcard = membership_card.generate_random()
    #         resp = self.client.post("/membership_cards", json=mcard, headers=headers)
    #         mcard_id = resp.json()["id"]
    #         self.client.patch(
    #             f"/payment_card/{pcard_id}/membership_card/{mcard_id}",
    #             headers=headers,
    #             name="/payment_card/<pcard_id>/membership_card/<mcard_id>",
    #         )


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    wait_time = constant(0)
