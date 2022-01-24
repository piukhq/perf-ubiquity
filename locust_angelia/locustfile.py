from locust import HttpUser, constant
from user_behaviour import UserBehavior

from locust_config import set_task_repeats
from vault import load_secrets


class WebsiteUser(HttpUser):

    load_secrets()

    """
    Repeats is a dictionary representing the total number of runs per task. i.e. 2 = task is run 2 times
    in total.
    ALL tasks to be run must be in this list and have the @repeatable_task decorator.
    """

    repeats = {
        "post_token": 1,
        "post_get_new_access_token_via_refresh": 1,
        "post_get_new_access_token_via_b2b": 1,
        "get_loyalty_plans": 1,
        "get_loyalty_plans_by_id": 1,
        "get_loyalty_plans_journey_fields_by_id": 1,
        "get_loyalty_plans_overview": 1,
        "stop_locust_after_test_suite": 1,
        "delete_me": 1,
    } 

    set_task_repeats(repeats)

    tasks = [UserBehavior]
    wait_time = constant(0)
