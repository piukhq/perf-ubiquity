import time
import uuid

import jwt

from settings import JWT_SECRET


def generate_auth_header(user_email, iat):
    secret = JWT_SECRET
    claims = {
        "bundle_id": "com.barclays.test",
        "iat": iat,
        "organisation_id": "Barclays",
        "property_id": "unused",
        "user_id": user_email,
    }
    token = jwt.encode(claims, secret, algorithm="HS512").decode("UTF-8")
    return {"Authorization": f"Bearer {token}"}


def generate_random():
    email_id = str(uuid.uuid4())
    return {"consent": {"email": f"performance-{email_id}@testbink.com", "timestamp": int(time.time())}}


def generate_static():
    return {"consent": {"email": f"performance-test@testbink.com", "timestamp": 1542189471}}
