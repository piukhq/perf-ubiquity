import random
import uuid

from shared_config_storage.credentials.encryption import RSACipher

from data_population.create_data.create_plan import SENSITIVE_FIELDS
from data_population.fixtures.membership_plan import CONSENT_LABEL
from settings import fake


PRE_REGISTERED_CARD_STATUS = 406


def static_add_json(pub_key):
    mcard_json = {
        "account": {
            "add_fields": [{"column": "Card Number", "value": "9000000000000000016"}],
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
            "add_fields": [{"column": "Card Number", "value": str(uuid.uuid4())}],
            "authorise_fields": [
                {"column": "Postcode", "value": fake.postcode()},
                {"column": CONSENT_LABEL, "value": "true"}
            ],
        },
        "membership_plan": plan_id,
    }

    return encrypt(mcard_json, pub_key)


def random_join_json(plan_id_list, pub_key):
    mcard_json = {
        "account": {
            "enrol_fields": [
                {"column": "Card Number", "value": str(uuid.uuid4())},
                {"column": "Postcode", "value": fake.postcode()}
            ]
        },
        "membership_plan": random.choice(plan_id_list)
    }

    return encrypt(mcard_json, pub_key)


def random_patch_json(pub_key):
    mcard_json = {
        "account": {
            "add_fields": [{"column": "Card Number", "value": str(uuid.uuid4())}]
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
