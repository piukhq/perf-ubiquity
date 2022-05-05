import logging
from enum import Enum
from functools import wraps

from locust import task

from request_data.locust_setup_requests import request_membership_plan_total

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Change this to specify how many channels the locust tests use
MEMBERSHIP_PLANS = request_membership_plan_total()
TOTAL_CLIENTS = 8
PCARD_DECRYPT_WAIT_TIME = 120
MULTIPLE_PROPERTY_PCARD_INDEX = 0
MULTIPLE_PROPERTY_MCARD_TOTAL = 4
PATCH_PLANS = range(1, MEMBERSHIP_PLANS + 1)[-2:]
NON_PATCH_PLANS = range(1, MEMBERSHIP_PLANS + 1)[:-2]

AUTOLINK = {"autolink": "true"}


TEST_SUITE = {
    # ubiquity tests
    "get_service": True,
    "post_membership_cards_single_property_join": True,
    "post_membership_cards_restricted_property_join": True,
    "get_membership_plans": True,
    "get_membership_plan_id": True,
    "post_membership_cards_single_property_add": True,
    "post_membership_cards_restricted_property_add": True,
    "post_membership_cards_single_property_add_ghost_cards": True,
    "post_payment_cards_single_property": True,
    "post_payment_cards_multiple_property": True,
    "get_membership_card_single_property": True,
    "get_membership_card_transactions_single_property": True,
    "patch_membership_card_id_payment_card_id_single_property": False,  # Barclays don't use this endpoint
    "patch_payment_card_id_membership_card_id_single_property": False,  # Barclays don't use this endpoint
    "post_membership_cards_multiple_property_restricted": True,
    "post_membership_cards_multiple_property": True,
    "patch_membership_card_id_payment_card_id_multiple_property": False,  # Barclays don't use this endpoint
    "patch_payment_card_id_membership_card_id_multiple_property": False,  # Barclays don't use this endpoint
    "get_membership_card_multiple_property": True,
    "get_membership_card_transactions_multiple_property": True,
    "get_payment_cards": True,
    "get_membership_cards": True,
    "patch_membership_cards_id_ghost": True,
    "patch_membership_cards_id_add": True,
    "delete_payment_card_multiple_property": True,
    "delete_payment_card_single_property": True,
    "delete_payment_card_by_hash_multiple_property": False,
    "delete_payment_card_by_hash_single_property": False,
    "delete_membership_card": True,
    "delete_service": True,
    # barclays specific tests
    "post_membership_cards": True,
    # config functions
    "stop_locust_after_test_suite": True,
}

repeat_tasks = {}  # values assigned by locustfile


def check_suite_whitelist(test_func):
    if TEST_SUITE.get(test_func.__name__):
        return test_func
    else:
        return lambda *args, **kwargs: None


def repeat_task(num: int):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(num):
                func(*args, **kwargs)
            return True

        return wrapper

    return decorator


def repeatable_task():
    def decorator(func):
        @wraps(func)
        @task
        def wrapper(*args, **kwargs):
            num = repeat_tasks.get(func.__name__, 0)
            for _ in range(num):
                func(*args, **kwargs)
            return True

        return wrapper

    return decorator


class LocustLabel(str, Enum):
    SINGLE_PROPERTY = "- Single property"
    MULTI_PROPERTY = "- Multi property"
    SINGLE_RESTRICTED_PROPERTY = "- Single restricted property"
    MULTI_RESTRICTED_PROPERTY = "- Multi restricted property"


def increment_locust_counter(count, max_count):
    new_count = (count % max_count) + 1
    return new_count


def set_task_repeats(repeats: dict):
    global repeat_tasks
    repeat_tasks = repeats
