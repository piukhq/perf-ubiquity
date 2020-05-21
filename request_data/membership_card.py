import uuid

from shared_config_storage.credentials.encryption import RSACipher

from data_population.create_data.create_plan import SENSITIVE_FIELDS
from data_population.fixtures.membership_plan import CONSENT_LABEL
from settings import fake


ACTIVE = 1
WALLET_ONLY = 10
PRE_REGISTERED_CARD_STATUS = 406
JOIN_FAILED = 900

GHOST_CARD_PREFIX = 0
NON_GHOST_CARD_PREFIX = 1


def card_number(ghost=False):
    if ghost:
        f"{GHOST_CARD_PREFIX}{uuid.uuid4()}"

    return f"{NON_GHOST_CARD_PREFIX}{uuid.uuid4()}"


def static_add_json(pub_key):
    mcard_json = {
        "account": {
            "add_fields": [{"column": "Card Number", "value": f"{NON_GHOST_CARD_PREFIX}000000000000000016"}],
            "authorise_fields": [
                {"column": "Postcode", "value": "rg5 5aa"},
                {"column": CONSENT_LABEL, "value": "true"}
            ],
        },
        "membership_plan": 1,
    }

    return encrypt(mcard_json, pub_key)


def random_add_json(plan_id, pub_key):
    mcard_json = {
        "account": {
            "add_fields": [{"column": "Card Number", "value": card_number()}],
            "authorise_fields": [
                {"column": "Postcode", "value": fake.postcode()},
                {"column": CONSENT_LABEL, "value": "true"}
            ],
        },
        "membership_plan": plan_id,
    }

    return encrypt(mcard_json, pub_key)


def random_add_ghost_card_json(plan_id, pub_key):
    mcard_json = {
        "account": {
            "add_fields": [{"column": "Card Number", "value": card_number(ghost=True)}],
            "authorise_fields": [
                {"column": "Postcode", "value": fake.postcode()},
                {"column": CONSENT_LABEL, "value": "true"}
            ],
        },
        "membership_plan": plan_id,
    }

    return encrypt(mcard_json, pub_key)


def random_join_json(plan_id, pub_key):
    mcard_json = {
        "account": {
            "enrol_fields": [
                {"column": "Card Number", "value": card_number()},
                {"column": "Postcode", "value": fake.postcode()}
            ]
        },
        "membership_plan": plan_id
    }

    return encrypt(mcard_json, pub_key)


def random_patch_json(pub_key):
    mcard_json = {
        "account": {
            "auth_fields": [{"column": "Postcode", "value": fake.postcode()}]
        }
    }

    return encrypt(mcard_json, pub_key)


def random_registration_json(pub_key):
    mcard_json = {
        "account": {
            "registration_fields": [
                {"column": "Postcode", "value": fake.postcode()}
            ]
        }
    }
    return encrypt(mcard_json, pub_key)


def encrypt(mcard, pub_key):
    for field_type, answers in mcard['account'].items():
        for answer in answers:
            if answer["column"] in SENSITIVE_FIELDS:
                answer["value"] = RSACipher().encrypt(answer["value"], pub_key=pub_key)

    return mcard
