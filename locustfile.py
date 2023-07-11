from locust import HttpUser, SequentialTaskSet, constant, task

from ubiquity_performance_test.locust_config import init_redis_events, spawn_completed

init_redis_events()


class UserBehavior(SequentialTaskSet):
    @task
    def call_lunaris(self) -> None:
        self.client.get("/test-scheme/balance")

    @task
    def stop_locust_after_test_suite(self) -> None:
        if spawn_completed():
            self.user.environment.runner.stop()

        while True:
            self._sleep(60)


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]  # noqa: RUF012
    wait_time = constant(0)
