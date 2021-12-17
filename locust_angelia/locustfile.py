from locust import HttpUser, constant
from user_behaviour import UserBehavior
from vault import load_secrets
from locust_config import configure_task_repeats


class WebsiteUser(HttpUser):

    load_secrets()

    repeats = {
        "get_new_token": 3
    }

    # Repeats is a dictionary representing the total number of runs per function. i.e. 2 = function is run 2 times
    # in total. If a function is not found in this list, it will default to 1 run, so only those functions that need be
    # repeated must have a value in this dict. ALL functions to be run must however have either the @task or
    # @repeatable_task decorator, or these will be ignored by locust.

    configure_task_repeats(repeats=repeats)

    tasks = [UserBehavior]
    wait_time = constant(0)
