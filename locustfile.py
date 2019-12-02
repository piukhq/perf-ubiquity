from locust import HttpLocust, TaskSet, task

from request_data import service, membership_card, payment_card
from settings import SCHEME_ID

WALLET_SIZE = 3


# total task weight: 5
class UserBehavior(TaskSet):

    def setup(self):
        consent = service.generate_static()
        email = consent['consent']['email']
        timestamp = consent['consent']['timestamp']
        self.test_headers = service.generate_auth_header(email, timestamp)
        self.client.post("/service", json=consent, headers=self.test_headers)

        resp = self.client.get("/membership_plans", headers=self.test_headers)
        membership_plan_ids = [str(plan['id']) for plan in resp.json()]
        if SCHEME_ID not in membership_plan_ids:
            raise ValueError(
                f"No performance test scheme in database (ID: {SCHEME_ID}), please run data population.."
            )

    def create_user(self):
        consent = service.generate_random()
        email = consent['consent']['email']
        timestamp = consent['consent']['timestamp']
        headers = service.generate_auth_header(email, timestamp)
        self.client.post("/service", json=consent, headers=headers)
        return headers

    @task(1)
    def get_service(self):
        headers = self.create_user()
        self.client.get("/service", headers=headers)

    @task(1)
    def get_membership_plans(self):
        self.client.get("/membership_plans", headers=self.test_headers)

    @task(1)
    def get_membership_plan(self):
        self.client.get(f"/membership_plan/{SCHEME_ID}", headers=self.test_headers, name="/membership_plan/<id>")

    @task(1)
    def populate_wallet_autolink(self):
        headers = self.create_user()
        params = {"autoLink": "True"}
        pcard = payment_card.generate_random()
        self.client.post("/payment_cards", json=pcard, headers=headers)

        for _ in range(0, WALLET_SIZE):
            mcard = membership_card.generate_random()
            self.client.post("/membership_cards", json=mcard, headers=headers, params=params)

    @task(1)
    def populate_wallet_manual(self):
        headers = self.create_user()
        mcard = membership_card.generate_random()
        resp = self.client.post("/membership_cards", json=mcard, headers=headers)
        mcard_id = resp.json()['id']

        pcard = payment_card.generate_random()
        resp = self.client.post("/payment_cards", json=pcard, headers=headers)
        pcard_id = resp.json()['id']

        self.client.patch(
            f"/membership_card/{mcard_id}/payment_card/{pcard_id}",
            headers=headers, name='/membership_card/<mcard_id>/payment_card/<pcard_id>'
        )

        for _ in range(0, WALLET_SIZE):
            mcard = membership_card.generate_random()
            resp = self.client.post("/membership_cards", json=mcard, headers=headers)
            mcard_id = resp.json()['id']
            self.client.patch(
                f"/payment_card/{pcard_id}/membership_card/{mcard_id}",
                headers=headers, name='/payment_card/<pcard_id>/membership_card/<mcard_id>'
            )


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
