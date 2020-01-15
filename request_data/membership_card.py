from settings import fake
from request_data.membership_plan import PlanIDs


def generate_random():
    return {
        "account": {
            "add_fields": [{"column": "Card Number", "value": str(fake.random.randint(1000000, 9999999))}],
            "authorise_fields": [{"column": "Postcode", "value": fake.postcode()}],
        },
        "membership_plan": PlanIDs.TEST_SCHEME_ID,
    }


def generate_static():
    return {
        "account": {
            "add_fields": [{"column": "Card Number", "value": "9000000000000000016"}],
            "authorise_fields": [{"column": "Postcode", "value": "rg5 5aa"}],
        },
        "membership_plan": PlanIDs.TEST_SCHEME_ID,
    }
