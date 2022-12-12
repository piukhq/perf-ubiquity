import json

STATIC_PCARD_HISTORY_BODY = json.dumps(
    {
        "id": 123,
        "hash": None,
        "order": 0,
        "token": "imatesttoken123",
        "issuer": 4,
        "status": 1,
        "country": "UK",
        "created": "2022-12-12T06:02:26.611664Z",
        "pan_end": "1111",
        "updated": "2022-12-12T06:02:26.669769Z",
        "consents": [],
        "pan_start": "421111",
        "psp_token": "imatesttoken123",
        "agent_data": {"card_uid": "123456-1234-1234-1234-123456"},
        "is_deleted": False,
        "start_year": None,
        "expiry_year": 2055,
        "fingerprint": "imatestfingerprint123",
        "issuer_name": "",
        "start_month": None,
        "expiry_month": 1,
        "name_on_card": "Jeff",
        "payment_card": 1,
        "card_nickname": "",
        "currency_code": "GBP",
    }
)
