from locust import HttpUser, constant, events
from user_behaviour import UserBehavior

from environment.angelia_token_generation import tokens
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
        # --TOKEN--
        "post_token": 1,  # REQUIRED
        "post_token_secondary_user": 1,  # REQUIRED
        "post_get_new_access_token_via_refresh": 1,
        "post_get_new_access_token_via_b2b": 1,
        # --LOYALTY_PLANS--
        "get_loyalty_plans": 0,
        "get_loyalty_plans_by_id": 0,
        "get_loyalty_plans_journey_fields_by_id": 0,
        "get_loyalty_plans_overview": 0,
        # --LOYALTY_CARDS--
        "post_loyalty_cards_add": 0,  # Single and Multiuser (1 each) - Adds 1 card
        "post_loyalty_cards_add_and_auth": 0,  # Single and Multiuser (1 each) - Adds 1 card
        "put_loyalty_cards_authorise": 0,  # Single user only                   ****BROKEN DO NOT USE!!!***
        "post_loyalty_cards_add_and_register": 0,  # Single and Multiuser (1 each) - Adds 1 card
        "post_loyalty_cards_join": 0,  # Single user only
        "delete_loyalty_card_by_id": 0,  # Should be less than total loyalty_cards added (or will 404)
        # --USER--
        "delete_me": 0,
        # --SPECIAL--
        "stop_locust_after_test_suite": 1,
    }

    set_task_repeats(repeats)

    tasks = [UserBehavior]
    wait_time = constant(0)


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("Test started")
    tokens.generate_tokens(environment)
