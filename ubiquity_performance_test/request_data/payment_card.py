import random
import string
import uuid
from enum import StrEnum

from shared_config_storage.credentials.encryption import RSACipher

from ubiquity_performance_test.settings import fake

FIELDS_TO_ENCRYPT = ("first_six_digits", "last_four_digits", "month", "year", "hash")


class PaymentProvider(StrEnum):
    AMEX = "37"
    MASTERCARD = "55"
    VISA = "42"


def generate_unencrypted_static() -> dict:
    return {
        "card": {
            "hash": "28OBFUDWPS4YX13WPA0ENXW96Z4X2EG9GXSIGJOD06ZV3XKX9MDG733NVPJR14TEHQEFVHKYVB2ETM3Z0UCQY4A8UCB8GPE67Z"
            "B87HP2J2QKKMYCMBN3CUH9NYE7R83N",
            "token": "9bd11390-b8e8-4627-baa0-c738645fb9b5",
            "last_four_digits": 3733,  # amex bin
            "first_six_digits": 466666,
            "name_on_card": "performance test static",
            "month": 1,
            "year": 2059,
            "fingerprint": "33df7b61-b908-4496-847c-c4bd280b26ef",
        },
        "account": {"consents": []},
    }


def generate_random_hash() -> str:
    return "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(128))


def generate_unencrypted_random() -> dict:
    random_four = str(random.randint(1000, 9999))
    card_bin = random.choice(list(PaymentProvider))
    return {
        "card": {
            "hash": generate_random_hash(),
            "token": str(uuid.uuid4()),
            "last_four_digits": random_four,
            "first_six_digits": f"{card_bin}{random_four}",
            "name_on_card": fake.name(),
            "month": 1,
            "year": 2059,
            "fingerprint": str(uuid.uuid4()),
        },
        "account": {"consents": []},
    }


def encrypt(pcard: dict, pub_key: str) -> dict:
    for field in FIELDS_TO_ENCRYPT:
        cred = pcard["card"].get(field)
        if not cred:
            raise ValueError(f"Missing credential {field}")
        try:
            encrypted_val = RSACipher().encrypt(cred, pub_key=pub_key)
        except Exception as e:
            raise ValueError(f"Value: {cred}") from e
        pcard["card"][field] = encrypted_val

    return pcard
