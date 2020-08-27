from locust import constant, task, HttpUser, SequentialTaskSet

from settings import SERVICE_API_KEY


class PostgresTest(SequentialTaskSet):
    auth_header = {
        "Authorization": f"Token {SERVICE_API_KEY}"
    }

    @task
    def call_postgres_test_endpoint(self):
        self.client.get("/postgres_test", headers=self.auth_header)


class WebsiteUser(HttpUser):
    tasks = [PostgresTest]
    wait_time = constant(0)
