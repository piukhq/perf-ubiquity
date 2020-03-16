import random
import uuid

from data_population.fixtures.membership_plan import CONSENT_LABEL
from settings import fake


def static_add_json():
    return {
        "account": {
            "add_fields": [{"column": "Card Number", "value": "9000000000000000016"}],
            "authorise_fields": [
                {"column": "Postcode", "value": "rg5 5aa"},
                {"column": CONSENT_LABEL, "value": "true"}
            ],
        },
        "membership_plan": 1,
    }


def random_add_json(plan_id):
    return {
        "account": {
            "add_fields": [{"column": "Card Number", "value": str(uuid.uuid4())}],
            "authorise_fields": [
                {"column": "Postcode", "value": fake.postcode()},
                {"column": CONSENT_LABEL, "value": "true"}
            ],
        },
        "membership_plan": plan_id,
    }


def random_join_json(plan_id_list):
    return {
        "account": {
            "enrol_fields": [
                {"column": "Card Number", "value": str(uuid.uuid4())},
                {"column": "Postcode", "value": fake.postcode()}
            ]
        },
        "membership_plan": random.choice(plan_id_list)
    }


def random_patch_json():
    return {
        "account": {
            "add_fields": [{"column": "Card Number", "value": str(uuid.uuid4())}]
        }
    }


def random_registration_json():
    return {
        "account": {
            "registration_fields": [
                {"column": "Card Number", "value": str(uuid.uuid4())},
                {"column": "Postcode", "value": fake.postcode()}
            ]
        }
    }
