import uuid


def generate_random_email_and_sub():
    sub = str(uuid.uuid4())
    return f"performance-{sub}@testbink.com", sub
