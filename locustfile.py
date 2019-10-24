from random import randint

from hashids import Hashids
from locust import HttpLocust, TaskSet, task

from fixtures import generate_mcard, generate_pcard

ALPHABET = "abcdefghijklmnopqrstuvwxyz1234567890"
hash_ids = Hashids(
    min_length=32, salt="pfNqP7AzQbitjGIv9SsD7pYKDBNvxkys", alphabet=ALPHABET
)


# total task weight: 153
class UserBehavior(TaskSet):

    def get_headers(self, service_id):
        service_token = hash_ids.encode(service_id)
        return {"Authorization": f"token {service_token}"}

    @task(105)
    def get_wallet(self):
        service_id = randint(1, 27000000)
        print(f"Get wallet with service id: {service_id}")
        self.client.get("/service", headers=self.get_headers(service_id))

    @task(41)
    def create_pcard(self):
        service_id = randint(1, 27000000)
        pcard = generate_pcard()
        print(f"Create payment card with service id: {service_id}")
        self.client.post("/payment_cards", json=pcard, headers=self.get_headers(service_id))

    @task(7)
    def create_mcard(self):
        service_id = randint(1, 27000000)
        mcard = generate_mcard()
        print(f"Create membership card with service id: {service_id}")
        self.client.post("/membership_cards", json=mcard, headers=self.get_headers(service_id))


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
