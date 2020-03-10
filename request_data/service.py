import time
import uuid

import jwt


def generate_auth_header(user_email, iat, client_fixture, secret):
    claims = {
        "bundle_id": client_fixture["bundle_id"],
        "iat": iat,
        "organisation_id": client_fixture["organisation_name"],
        "property_id": "unused",
        "user_id": user_email,
    }
    token = jwt.encode(claims, secret, algorithm="HS512").decode("UTF-8")
    return {"Authorization": f"Bearer {token}"}


def generate_random():
    email_id = str(uuid.uuid4())
    return {
        "consent": {
            "email": f"performance-{email_id}@testbink.com",
            "timestamp": int(time.time()),
        }
    }


def generate_static():
    return {
        "consent": {"email": f"performance-test@testbink.com", "timestamp": 1542189471}
    }
