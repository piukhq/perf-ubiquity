import json
import logging
from enum import Enum
from functools import wraps
from time import sleep

from shared_config_storage.vault import secrets

from request_data.locust_setup_requests import request_membership_plan_total
from settings import (
    CHANNEL_VAULT_PATH,
    LOCAL_SECRETS,
    LOCAL_SECRETS_PATH,
    VAULT_TOKEN,
    VAULT_URL,
)


class VaultException(Exception):
    pass


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

channel_info = None


# Change this to specify how many channels the locust tests use
MEMBERSHIP_PLANS = request_membership_plan_total()
TOTAL_CLIENTS = 6
PCARD_DECRYPT_WAIT_TIME = 120
MULTIPLE_PROPERTY_PCARD_INDEX = 0
MULTIPLE_PROPERTY_MCARD_TOTAL = 4
PATCH_PLANS = range(1, MEMBERSHIP_PLANS + 1)[-2:]
NON_PATCH_PLANS = range(1, MEMBERSHIP_PLANS + 1)[:-2]

AUTOLINK = {"autolink": "true"}


TEST_SUITE = {
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
    "delete_membership_card": True,
    "delete_service": True,
    "stop_locust_after_test_suite": True,
    # barclays specific tests
    "post_membership_cards": True,
}


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


class LocustLabel(str, Enum):
    SINGLE_PROPERTY = "- Single property"
    MULTI_PROPERTY = "- Multi property"
    SINGLE_RESTRICTED_PROPERTY = "- Single restricted property"
    MULTI_RESTRICTED_PROPERTY = "- Multi restricted property"


def increment_locust_counter(count, max_count):
    new_count = (count % max_count) + 1
    return new_count


def _read_vault_with_retry() -> dict:
    for i in range(1, 3):
        try:
            channel_info = secrets.read_vault(CHANNEL_VAULT_PATH, VAULT_URL, VAULT_TOKEN)
            if not channel_info:
                raise secrets.VaultError("Vault returned empty channel_info")

        except secrets.VaultError:
            logger.warning("VaultError: failed to read from vault.")
            sleep(3 * i)
        else:
            logger.info("collected channel_info: {channel_info}")
            return channel_info

    raise VaultException("Failed to read from the Vault even after 3 retries.")


def load_secrets():
    global channel_info
    if channel_info is None:
        if LOCAL_SECRETS:
            with open(LOCAL_SECRETS_PATH) as fp:
                channel_info = json.load(fp)
        else:
            channel_info = _read_vault_with_retry()

    return channel_info
