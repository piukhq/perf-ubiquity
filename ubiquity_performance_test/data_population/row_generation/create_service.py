import random
import uuid

import arrow

from ubiquity_performance_test.data_population.fixtures.client import ALL_CLIENTS
from ubiquity_performance_test.data_population.fixtures.user import STATIC_USER_HISTORY_BODY


def user(user_id: int) -> list:
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
        client["client_id"],  # client_id
        "abcdefgh",  # salt
        user_email,  # external_id
        False,  # is_tester
        "NULL",  # apple
        "",  # delete_token
        "NULL",  # magic_link_verified
        client["bundle_id"],  # (originating)bundle_id
        "NULL",  # last_accessed
    ]


def historic_user(history_id: int) -> list:
    return [
        history_id,  # id
        "2019-03-12 15:51:36.390742+00",  # created
        "create",  # change_type
        history_id,  # instance_id
        "internal_service",  # channel
        "",  # change_details
        STATIC_USER_HISTORY_BODY,  # body
        "robojeff@testbink.com",  # email
        "1234567890",  # external_id
        arrow.now(),  # event_time
        "NULL",  # uuid
    ]


def service(user_id: int) -> list:
    return [user_id, "NULL", "NULL", "2020-03-09 12:42:15+00"]  # id  # latitude  # longitude  # timestamp
