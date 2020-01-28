import uuid

from settings import fake
from request_data.membership_plan import PlanIDs


def static_add_json():
    return {
        "account": {
            "add_fields": [{"column": "Card Number", "value": "9000000000000000016"}],
            "authorise_fields": [{"column": "Postcode", "value": "rg5 5aa"}],
        },
        "membership_plan": PlanIDs.TEST_SCHEME_ID,
    }


def random_add_json():
    return {
        "account": {
            "add_fields": [{"column": "Card Number", "value": str(uuid.uuid4())}],
            "authorise_fields": [{"column": "Postcode", "value": fake.postcode()}],
        },
        "membership_plan": PlanIDs.TEST_SCHEME_ID,
    }


def random_join_json():
    return {
        "account": {
            "enrol_fields": [
                {"column": "Card Number", "value": str(uuid.uuid4())},
                {"column": "Postcode", "value": fake.postcode()}
            ]
        },
        "membership_plan": PlanIDs.TEST_SCHEME_ID,
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
