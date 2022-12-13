import json

STATIC_USER_HISTORY_BODY = json.dumps(
    {
        "id": 1,
        "uid": "123456-1234-1234-1234-123456",
        "salt": "abcdefgh",
        "apple": None,
        "email": "robojeff@bink.com",
        "client": "performance_one",
        "twitter": None,
        "facebook": None,
        "is_staff": False,
        "password": "275358a0-ed5f-4807-a775-9ce5aeb3c19c",
        "bundle_id": "performance.bundle.one",
        "is_active": True,
        "is_tester": False,
        "last_login": None,
        "date_joined": "2022-01-01T01:01:01.000001Z",
        "external_id": "blah1234",
        "reset_token": None,
        "delete_token": "",
        "is_superuser": False,
        "last_accessed": "2022-01-01T01:01:01.000001+00:00",
        "marketing_code": None,
        "magic_link_verified": None,
    }
)
