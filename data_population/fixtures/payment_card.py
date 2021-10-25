import json

STATIC_PCARD_HISTORY_BODY = json.dumps(
    {
        "id": 123,
        "hash": None,
        "order": 0,
        "token": "testtoken123",
        "issuer": 4,
        "status": 0,
        "country": "UK",
        "created": "2020-11-19T11:14:33.911729Z",
        "pan_end": "1111",
        "updated": "2020-11-19T11:14:33.911865Z",
        "consents": [],
        "user_set": [123],
        "pan_start": "421111",
        "pll_links": [],
        "psp_token": "testtoken123",
        "agent_data": {},
        "is_deleted": False,
        "start_year": None,
        "expiry_year": 2022,
        "fingerprint": "testfingerprint123",
        "start_month": None,
        "expiry_month": 2,
        "name_on_card": "jeff",
        "payment_card": 1,
        "currency_code": "GBP",
        "formatted_images": {},
        "scheme_account_set": [123],
    }
)
