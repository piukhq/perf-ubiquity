from locust import constant, task, HttpUser, SequentialTaskSet


SERVICE_KEY = "F616CE5C88744DD52DB628FAD8B3D"


class PostgresTest(SequentialTaskSet):

    def auth_header(self):
        return {
            "Authorization": f"Token {SERVICE_KEY}"
        }

    @task
    def call_postgres_test_endpoint(self):
        self.client.get("/postgres_test", headers=self.auth_header())


class WebsiteUser(HttpUser):
    tasks = [PostgresTest]
    wait_time = constant(0)
