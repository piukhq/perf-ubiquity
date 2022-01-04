from locust import HttpUser, constant
from user_behaviour import UserBehavior
from vault import load_secrets
from locust_config import set_task_repeats


class WebsiteUser(HttpUser):

    load_secrets()

    """
    Repeats is a dictionary representing the total number of runs per task. i.e. 2 = task is run 2 times
    in total. 
    
    ALL tasks to be run must be in this list and have the @repeatable_task decorator.
    """

    repeats = {
        "post_token": 1,
        "get_new_token": 4,  # Randomly chooses between calling post_token endpoint again as above, or via refresh.
        "stop_locust_after_test_suite": 1
    }

    set_task_repeats(repeats)

    tasks = [UserBehavior]
    wait_time = constant(0)
