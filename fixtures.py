import time
import uuid

from faker import Faker

fake = Faker("en_GB")


def generate_mcard():
    return {
        "account": {
            "add_fields": [
                {
                    "column": "Card Number",
                    "value": str(fake.random.randint(1000000, 9999999))
                }
            ],
            "authorise_fields": [
                {
                    "column": "Last Name",
                    "value": fake.last_name()
                },
                {
                    "column": "Postcode",
                    "value": fake.postcode()
                }
            ]
        },
        "membership_plan": fake.random.randint(1, 200)
    }


def generate_pcard():
    return {
        "card": {
            "token": str(uuid.uuid4()),
            "last_four_digits": fake.random.randint(1000, 9999),
            "first_six_digits": fake.random.randint(100000, 999999),
            "name_on_card": fake.name(),
            "month": 1,
            "year": 2059,
            "fingerprint": str(uuid.uuid4())
        },
        "account": {
            "consents": [{
                "latitude": 51.405372,
                "longitude": -0.678357,
                "timestamp": int(time.time()),
                "type": 2
            }]
        }
    }
