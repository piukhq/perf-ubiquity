from settings import fake, SCHEME_ID


def generate_random():
    return {
        "account": {
            "add_fields": [{"column": "Card Number", "value": str(fake.random.randint(1000000, 9999999))}],
            "authorise_fields": [{"column": "Postcode", "value": fake.postcode()}],
        },
        "membership_plan": SCHEME_ID,
    }


def generate_static():
    return {
        "account": {
            "add_fields": [{"column": "Card Number", "value": "9000000000000000016"}],
            "authorise_fields": [{"column": "Postcode", "value": "rg5 5aa"}],
        },
        "membership_plan": SCHEME_ID,
    }
