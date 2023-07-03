import uuid


def generate_random_email_and_sub() -> tuple[str, str]:
    sub = str(uuid.uuid4())
    return f"performance-{sub}@testbink.com", sub
