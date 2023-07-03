import uuid

from shared_config_storage.credentials.encryption import RSACipher

from ubiquity_performance_test.data_population.fixtures.membership_plan import CONSENT_LABEL
from ubiquity_performance_test.data_population.row_generation.create_plan import SENSITIVE_FIELDS
from ubiquity_performance_test.settings import fake

ACTIVE = 1
WALLET_ONLY = 10
PRE_REGISTERED_CARD_STATUS = 406
JOIN_FAILED = 900

GHOST_CARD_PREFIX = 0
NON_GHOST_CARD_PREFIX = 1


def card_number(ghost: bool = False) -> str:
    if ghost:
        return f"{GHOST_CARD_PREFIX}{uuid.uuid4()}"

    return f"{NON_GHOST_CARD_PREFIX}{uuid.uuid4()}"


def static_add_json(pub_key: str) -> dict:
    mcard_json = {
        "account": {
            "add_fields": [{"column": "Card Number", "value": f"{NON_GHOST_CARD_PREFIX}000000000000000016"}],
            "authorise_fields": [
                {"column": "Password", "value": "testpassword123"},
                {"column": CONSENT_LABEL, "value": "true"},
            ],
        },
        "membership_plan": 1,
    }

    return encrypt(mcard_json, pub_key)


def random_add_json(plan_id: int, pub_key: str) -> dict:
    mcard_json = {
        "account": {
            "add_fields": [{"column": "Card Number", "value": card_number()}],
            "authorise_fields": [
                {"column": "Password", "value": fake.password()},
                {"column": CONSENT_LABEL, "value": "true"},
            ],
        },
        "membership_plan": plan_id,
    }

    return encrypt(mcard_json, pub_key)


def random_add_ghost_card_json(plan_id: int, pub_key: str) -> dict:
    mcard_json = {
        "account": {
            "add_fields": [{"column": "Card Number", "value": card_number(ghost=True)}],
            "authorise_fields": [
                {"column": "Password", "value": fake.password()},
                {"column": CONSENT_LABEL, "value": "true"},
            ],
        },
        "membership_plan": plan_id,
    }

    return encrypt(mcard_json, pub_key)


def random_join_json(plan_id: int, pub_key: str) -> dict:
    mcard_json = {
        "account": {
            "enrol_fields": [
                {"column": "Password", "value": fake.password()},
                {"column": "First name", "value": fake.first_name()},
            ]
        },
        "membership_plan": plan_id,
    }

    return encrypt(mcard_json, pub_key)


def random_patch_json(pub_key: str) -> dict:
    mcard_json = {"account": {"auth_fields": [{"column": "Password", "value": fake.password()}]}}

    return encrypt(mcard_json, pub_key)


def random_registration_json(pub_key: str) -> dict:
    mcard_json = {
        "account": {
            "registration_fields": [
                {"column": "Password", "value": fake.password()},
                {"column": "First name", "value": fake.first_name()},
            ]
        }
    }
    return encrypt(mcard_json, pub_key)


def convert_enrol_to_add_json(enrol_json: dict) -> dict:
    enrol_credentials = {cred["column"]: cred["value"] for cred in enrol_json["account"]["enrol_fields"]}
    return {
        "account": {
            "add_fields": [{"column": "Card Number", "value": enrol_credentials["Card Number"]}],
            "authorise_fields": [
                {"column": "Password", "value": enrol_credentials["Password"]},
                {"column": CONSENT_LABEL, "value": "true"},
            ],
        },
        "membership_plan": enrol_json["membership_plan"],
    }


def encrypt(mcard: dict, pub_key: str) -> dict:
    for _field_type, answers in mcard["account"].items():
        for answer in answers:
            if answer["column"] in SENSITIVE_FIELDS:
                answer["value"] = RSACipher().encrypt(answer["value"], pub_key=pub_key)

    return mcard
