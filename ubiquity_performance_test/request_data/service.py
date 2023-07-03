import time
import uuid
from typing import TYPE_CHECKING

import jwt

if TYPE_CHECKING:
    from typing import TypedDict

    from ubiquity_performance_test.data_population.fixtures.client import ClientType

    class _ConsentPayloadType(TypedDict):
        email: str
        timestamp: int

    class ConsentType(TypedDict, total=False):
        consent: _ConsentPayloadType


def generate_auth_header(user_email: str, iat: int, client_fixture: "ClientType", secret: str) -> dict[str, str]:
    claims = {
        "bundle_id": client_fixture["bundle_id"],
        "iat": iat,
        "organisation_id": client_fixture["organisation_name"],
        "property_id": "unused",
        "user_id": user_email,
    }
    token = jwt.encode(claims, secret, algorithm="HS512")

    return {"Authorization": f"Bearer {token}", "Accept": "application/json;v=1.2"}


def generate_random() -> "ConsentType":
    email_id = str(uuid.uuid4())
    return {
        "consent": {
            "email": f"performance-{email_id}@testbink.com",
            "timestamp": int(time.time()),
        }
    }


def generate_setup_user() -> "ConsentType":
    return {
        "consent": {
            "email": "performance-test@bink.com",
            "timestamp": int(time.time()),
        }
    }
