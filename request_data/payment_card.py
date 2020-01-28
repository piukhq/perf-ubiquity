import random
import time
import uuid
from enum import IntEnum

from shared_config_storage.credentials.encryption import RSACipher

from request_data.membership_plan import ClientBundleIDs
from settings import fake, VAULT_URL, VAULT_TOKEN

FIELDS_TO_ENCRYPT = (
    'first_six_digits',
    'last_four_digits',
    'month',
    'year',
    'hash'
)


class PaymentProvider(IntEnum):
    AMEX = "37"
    MASTERCARD = "55"
    VISA = "42"


def generate_unencrypted_random():
    random_four = str(random.randint(1000, 9999))
    card_bin = random.choice(list(PaymentProvider))
    return {
        "card": {
            "token": str(uuid.uuid4()),
            "last_four_digits": random_four,
            "first_six_digits": f"{card_bin}{random_four}",
            "name_on_card": fake.name(),
            "month": 1,
            "year": 2059,
            "fingerprint": str(uuid.uuid4()),
        },
        "account": {
            "consents": [
                {
                    "latitude": 51.405372,
                    "longitude": -0.678357,
                    "timestamp": int(time.time()),
                    "type": 2,
                }
            ]
        },
    }


def generate_random():
    pcard = generate_unencrypted_random()
    rsa = RSACipher(VAULT_TOKEN, VAULT_URL, ClientBundleIDs.BARCLAYS)
    for field in FIELDS_TO_ENCRYPT:
        cred = pcard['card'].get(field)
        if not cred:
            raise ValueError(f"Missing credential {field}")
        try:
            encrypted_val = rsa.encrypt(cred)
        except Exception as e:
            raise ValueError(f"Value: {cred}") from e
        pcard['card'][field] = encrypted_val

    return pcard


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
        "account": {
            "consents": [
                {
                    "latitude": 51.405372,
                    "longitude": -0.678357,
                    "timestamp": 1573658810,
                    "type": 2,
                }
            ]
        },
    }