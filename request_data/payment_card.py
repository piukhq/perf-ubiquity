import time
import uuid

from settings import fake


def generate_random():
    return {
        "card": {
            "token": str(uuid.uuid4()),
            "last_four_digits": fake.random.randint(1000, 9999),
            "first_six_digits": fake.random.randint(400000, 499999),
            "name_on_card": fake.name(),
            "month": 1,
            "year": 2059,
            "fingerprint": str(uuid.uuid4()),
        },
        "account": {
            "consents": [{"latitude": 51.405372, "longitude": -0.678357, "timestamp": int(time.time()), "type": 2}]
        },
    }


def generate_static():
    return {
        "card": {
            "token": "0d9eb69c-9739-4ed6-9751-c2a53082572f",
            "last_four_digits": 1111,
            "first_six_digits": 466666,
            "name_on_card": "test",
            "month": 1,
            "year": 2059,
            "fingerprint": "262154d2-7cdd-43dc-a285-397e35444292",
        },
        "account": {"consents": [{"latitude": 51.405372, "longitude": -0.678357, "timestamp": 1573658810, "type": 2}]},
    }
