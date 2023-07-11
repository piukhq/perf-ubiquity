from collections.abc import Callable
from enum import StrEnum
from functools import wraps
from typing import Any

from locust import events, task
from locust.env import Environment

from ubiquity_performance_test.request_data.locust_setup_requests import request_membership_plan_total
from ubiquity_performance_test.settings import REDIS_SPAWN_COMPLETED_KEY, redis

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
    "delete_payment_card_multiple_property": False,
    "delete_payment_card_single_property": False,
    "delete_payment_card_by_hash_multiple_property": True,
    "delete_payment_card_by_hash_single_property": True,
    "delete_membership_card": True,
    "delete_service": True,
    # barclays specific tests
    "post_membership_cards": True,
    # config functions
    "stop_locust_after_test_suite": True,
}

repeat_tasks: dict = {}  # values assigned by locustfile


def check_suite_whitelist(test_func: Callable) -> Callable:
    if TEST_SUITE.get(test_func.__name__):
        return test_func

    return lambda *args, **kwargs: None  # noqa: ARG005


def repeat_task(num: int) -> Callable:
    def decorator(func: Callable) -> Callable[..., bool]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> bool:  # noqa: ANN401
            for _ in range(num):
                func(*args, **kwargs)
            return True

        return wrapper

    return decorator


def repeatable_task() -> Callable:
    def decorator(func: Callable) -> Callable[..., bool]:
        @wraps(func)  # type: ignore [type-var]
        @task
        def wrapper(*args: Any, **kwargs: Any) -> bool:  # noqa: ANN401
            num = repeat_tasks.get(func.__name__, 0)
            for _ in range(num):
                func(*args, **kwargs)
            return True

        return wrapper

    return decorator


class LocustLabel(StrEnum):
    SINGLE_PROPERTY = "- Single property"
    MULTI_PROPERTY = "- Multi property"
    SINGLE_RESTRICTED_PROPERTY = "- Single restricted property"
    MULTI_RESTRICTED_PROPERTY = "- Multi restricted property"


def increment_locust_counter(count: int, max_count: int) -> int:
    new_count = (count % max_count) + 1
    return new_count


def set_task_repeats(repeats: dict) -> None:
    global repeat_tasks  # noqa: PLW0603
    repeat_tasks = repeats


def init_redis_events() -> None:
    def delete_redis_cache(environment: Environment) -> None:  # noqa: ARG001
        redis.delete(REDIS_SPAWN_COMPLETED_KEY)

    events.test_start.add_listener(delete_redis_cache)
    events.test_stop.add_listener(delete_redis_cache)

    @events.spawning_complete.add_listener
    def on_spawning_complete(user_count: int) -> None:  # noqa: ARG001
        redis.set(REDIS_SPAWN_COMPLETED_KEY, 1)


def spawn_completed() -> bool:
    return bool(redis.get(REDIS_SPAWN_COMPLETED_KEY))
