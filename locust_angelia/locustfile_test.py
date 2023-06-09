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
    TOTAL_TRUSTED_CHANNELS = 1
    RETRY_TIME = 0.5
    TIMEOUT = 10

    repeats = {
        # --TOKEN--
        "post_token": 1,  # REQUIRED
        "post_token_secondary_user": 0,  # REQUIRED
        "post_token_trusted_channel_primary_user": 0,  # REQUIRED
        "post_token_trusted_channel_secondary_user": 0,  # REQUIRED
        "post_get_new_access_token_via_refresh": 0,
        # --LOYALTY_PLANS--
        "get_loyalty_plans": 0,
        "get_loyalty_plans_by_id": 0,
        "get_loyalty_plans_journey_fields_by_id": 0,
        "get_loyalty_plans_overview": 0,
        # --LOYALTY_CARDS--
        "post_loyalty_cards_add": 0,  # Single and Multiuser (1 each) - Adds 1 card
        "post_loyalty_cards_trusted_add": 0,  # Single and Multiuser (1 each) - Adds 1 card
        "post_loyalty_cards_add_and_auth": 0,  # Single and Multiuser (1 each) - Adds 1 card
        "put_loyalty_cards_authorise": 0,  # Will 404 if > post_loyalty_cards_add
        "put_loyalty_cards_trusted_channel": 0,  # Will 404 if > post_loyalty_cards_trusted_add
        "post_loyalty_cards_add_and_register": 0,  # # Single User (1 each) - Adds 1 card
        "put_loyalty_cards_register": 0,  # Will 404 if > (post_loyalty_cards_add - put_authorise)
        "post_loyalty_cards_join": 0,
        "put_loyalty_cards_join": 0,
        "get_loyalty_cards_vouchers": 0,
        "get_loyalty_cards_transactions": 0,
        "get_loyalty_cards_balance": 0,
        # --PAYMENT_ACCOUNTS--
        "post_payment_account": 0,  # Single and Multiuser (1 each) - Adds 1 card
        "patch_payment_account": 0,  # Will 404 if no post_payment_account
        # --WALLET--
        "get_wallet": 0,
        "get_wallet_trusted_channel": 0,
        "get_wallet_overview": 0,
        "get_wallet_overview_trusted_channel": 0,
        "get_trusted_channel_payment_account_channel_links": 0,
        "get_wallet_loyalty_card": 0,  # Will 404 if no loyalty cards
        # --DELETE--
        "delete_join": 0,  # Should be less than total joins (or will 404)
        "delete_loyalty_card": 0,  # Should be less than total loyalty_cards added (or will 404)
        "delete_trusted_loyalty_card": 0,  # Should be less than total trusted_loyalty_cards added (or will 404)
        "delete_payment_account": 0,  # Will 404 if > post_payment_account
        # --USER--
        "post_email_update": 0,
        "delete_me": 0,
        # --SPECIAL--
        "stop_locust_after_test_suite": 1,
    }

    set_channels(TOTAL_CHANNELS, TOTAL_TRUSTED_CHANNELS)
    set_task_repeats(repeats)
    set_retry_and_timeout(retry_time_value=RETRY_TIME, timeout_value=TIMEOUT)

    tasks = [UserBehavior]
    wait_time = constant(0)


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("Test started")
    tokens.generate_tokens(environment)
