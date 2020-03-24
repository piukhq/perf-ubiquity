import random
import uuid
from enum import IntEnum

from shared_config_storage.credentials.encryption import RSACipher

from settings import fake

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


def generate_unencrypted_static():
    return {
        "card": {
            "hash": "8cfecd65-73a5-4e78-b8a7-ccffb33a8762",
            "token": "9bd11390-b8e8-4627-baa0-c738645fb9b5",
            "last_four_digits": 3733,  # amex bin
            "first_six_digits": 466666,
            "name_on_card": "performance test static",
            "month": 1,
            "year": 2059,
            "fingerprint": "33df7b61-b908-4496-847c-c4bd280b26ef",
        },
        "account": {
            "consents": []
        },
    }


def generate_unencrypted_random():
    random_four = str(random.randint(1000, 9999))
    card_bin = random.choice(list(PaymentProvider))
    return {
        "card": {
            "hash": str(uuid.uuid4()),
            "token": str(uuid.uuid4()),
            "last_four_digits": random_four,
            "first_six_digits": int(f"{card_bin}{random_four}"),
            "name_on_card": fake.name(),
            "month": 1,
            "year": 2059,
            "fingerprint": str(uuid.uuid4()),
        },
        "account": {
            "consents": []
        },
    }


def encrypt(pcard, pub_key):
    for field in FIELDS_TO_ENCRYPT:
        cred = pcard['card'].get(field)
        if not cred:
            raise ValueError(f"Missing credential {field}")
        try:
            encrypted_val = RSACipher().encrypt(cred, pub_key=pub_key)
        except Exception as e:
            raise ValueError(f"Value: {cred}") from e
        pcard['card'][field] = encrypted_val

    return pcard
