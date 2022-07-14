from locust import HttpUser, constant, events
from user_behaviour import UserBehavior, set_retry_and_timeout

from environment.angelia_token_generation import set_channels, tokens
from locust_config import set_task_repeats
from vault import load_secrets


class WebsiteUser(HttpUser):

    load_secrets()

    """
    Repeats is a dictionary representing the total number of runs per task. i.e. 2 = task is run 2 times
    in total.
    ALL tasks to be run must be in this list and have the @repeatable_task decorator.
    """

    TOTAL_CHANNELS = 8
    RETRY_TIME = 1
    TIMEOUT = 30

    repeats = {
        # --TOKEN--
        "post_token": 1,  # REQUIRED
        "post_token_secondary_user": 1,  # REQUIRED
        "post_get_new_access_token_via_refresh": 1,
        # --LOYALTY_PLANS--
        "get_loyalty_plans": 6,
        "get_loyalty_plans_by_id": 1,
        "get_loyalty_plans_journey_fields_by_id": 1,
        "get_loyalty_plan_details_by_id": 1,
        "get_loyalty_plans_overview": 3,
        # --LOYALTY_CARDS--
        "post_loyalty_cards_add": 2,  # Single and Multiuser (1 each) - Adds 1 card
        "post_loyalty_cards_add_and_auth": 1,  # Single and Multiuser (1 each) - Adds 1 card
        "put_loyalty_cards_authorise": 1,  # Will 404 if > post_loyalty_cards_add
        "post_loyalty_cards_add_and_register": 1,  # Single  User - Adds 1 card
        "put_loyalty_cards_register": 1,  # Will 404 if > (post_loyalty_cards_add - put_authorise)
        "post_loyalty_cards_join": 1,
        "get_loyalty_cards_vouchers": 1,
        "get_loyalty_cards_transactions": 1,
        "get_loyalty_cards_balance": 1,
        # --PAYMENT_ACCOUNTS--
        "post_payment_account": 1,  # Single and Multiuser (1 each) - Adds 1 card
        "patch_payment_account": 1,  # Will 404 if no post_payment_account
        # --WALLET--
        "get_wallet": 6,
        "get_wallet_overview": 3,
        "get_wallet_loyalty_card": 1,  # Will 404 if no loyalty cards
        # --DELETE--
        "delete_join": 1,  # Should be less than total joins (or will 404)
        "delete_loyalty_card": 1,  # Should be less than total loyalty_cards added (or will 404)
        "delete_payment_account": 1,  # Will 404 if > post_payment_account
        # --USER--
        "post_email_update": 1,
        "delete_me": 1,
        # --SPECIAL--
        "stop_locust_after_test_suite": 1,
    }

    set_channels(TOTAL_CHANNELS)
    set_task_repeats(repeats)
    set_retry_and_timeout(retry_time_value=RETRY_TIME, timeout_value=TIMEOUT)

    tasks = [UserBehavior]
    wait_time = constant(0)


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("Test started")
    tokens.generate_tokens(environment)
