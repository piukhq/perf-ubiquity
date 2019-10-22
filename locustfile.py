from hashids import Hashids
from locust import HttpLocust, TaskSet, task

from fixtures import generate_mcard, generate_pcard

ALPHABET = "abcdefghijklmnopqrstuvwxyz1234567890"
hash_ids = Hashids(
    min_length=32, salt="pfNqP7AzQbitjGIv9SsD7pYKDBNvxkys", alphabet=ALPHABET
)

SERVICE_ID = 1
MCARD_SERVICE_ID = 1
PCARD_SERVICE_ID = 1


# total task weight: 153
class UserBehavior(TaskSet):

    def get_headers(self, service_id):
        service_token = hash_ids.encode(service_id)
        return {"Authorization": f"token {service_token}"}

    @task(105)
    def get_wallet(self):
        global SERVICE_ID
        SERVICE_ID += 1
        print(f"Get wallet with service id: {SERVICE_ID}")
        self.client.get("/service", headers=self.get_headers(SERVICE_ID))

    @task(41)
    def create_pcard(self):
        global PCARD_SERVICE_ID
        PCARD_SERVICE_ID += 1
        pcard = generate_pcard()
        print(f"Create payment card with service id: {PCARD_SERVICE_ID}")
        self.client.post("/payment_cards", json=pcard, headers=self.get_headers(PCARD_SERVICE_ID))

    @task(7)
    def create_mcard(self):
        global MCARD_SERVICE_ID
        MCARD_SERVICE_ID += 1
        mcard = generate_mcard()
        print(f"Create membership card with service id: {MCARD_SERVICE_ID}")
        self.client.post("/membership_cards", json=mcard, headers=self.get_headers(MCARD_SERVICE_ID))


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
