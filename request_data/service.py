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
    token = jwt.encode(claims, secret, algorithm="HS512")

    return {"Authorization": f"Bearer {token}", "Accept": "application/json;v=1.2"}


def generate_random():
    email_id = str(uuid.uuid4())
    return {
        "consent": {
            "email": f"performance-{email_id}@testbink.com",
            "timestamp": int(time.time()),
        }
    }


def generate_setup_user():
    return {"consent": {"email": "performance-test@bink.com", "timestamp": int(time.time())}}
