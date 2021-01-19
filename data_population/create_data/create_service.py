import random
import uuid

from data_population.fixtures.client import ALL_CLIENTS


def user(user_id):
    user_uuid = str(uuid.uuid4())
    user_email = f"{user_uuid}@bink.com"
    client = random.choice(ALL_CLIENTS)
    return [
        user_id,  # id
        user_uuid,  # password
        "NULL",  # last_login
        False,  # is_superuser
        user_email,  # email
        True,  # is_active
        "2020-03-09 12:42:15+00",  # date_joined
        False,  # is_staff
        user_uuid,  # uid
        "NULL",  # facebook
        "NULL",  # twitter
        "NULL",  # reset_token
        "NULL",  # marketing_code_id
        client['client_id'],  # client_id
        "abcdefgh",  # salt
        user_email,  # external_id
        False,  # is_tester
        "NULL",  # apple
        "",  # delete_token
    ]


def service(user_id):
    return [
        user_id,  # id
        "NULL",  # latitude
        "NULL",  # longitude
        "2020-03-09 12:42:15+00"  # timestamp
    ]
