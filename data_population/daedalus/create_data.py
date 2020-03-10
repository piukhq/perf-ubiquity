import json
import uuid


def membership_plan(plan_id, name, slug):
    return [
        plan_id,  # id
        json.dumps({
            "plan_name": name,
            "plan_documents": [
                {
                    "name": "Terms & conditions",
                    "checkbox": True,
                    "url": "https://goo.gl/u72nN9",
                    "display": [
                        "REGISTRATION",
                        "ENROL"
                    ],
                    "description": "Terms & conditions"
                }
            ],
            "company_url": "https://goo.gl/xPNXKv",
            "plan_description": "Test plan description",
            "tiers": [],
            "add_fields": [
                {
                    "choice": [],
                    "validation": "(.*)",
                    "column": "Card Number",
                    "type": 0,
                    "common_name": "card_number"
                }
            ],
            "registration_fields": [
                {
                    "choice": [],
                    "validation": "(.*)",
                    "column": "Card Number",
                    "type": 0,
                    "common_name": "card_number"
                },
                {
                    "choice": [],
                    "validation": "(.*)",
                    "column": "Postcode",
                    "type": 0,
                    "common_name": "postcode"
                }
            ],
            "plan_name_card": "Performance Test",
            "fees": [
                {
                    "type": "enrolment",
                    "amount": 1.1
                }
            ],
            "enrol_incentive": "Placeholder Enrol Incentive",
            "category": "Household",
            "company_name": "company",
            "plan_register_info": "Registrations typically processed in 24hrs",
            "enrol_fields": [
                {
                    "choice": [],
                    "validation": "(.*)",
                    "column": "Card Number",
                    "type": 0,
                    "common_name": "card_number"
                },
                {
                    "choice": [],
                    "validation": "(.*)",
                    "column": "Postcode",
                    "type": 0,
                    "common_name": "postcode"
                }
            ],
            "plan_summary": "Test plan summary",
            "authorise_fields": [
                {
                    "choice": [],
                    "validation": "(.*)",
                    "column": "Postcode",
                    "type": 0,
                    "common_name": "postcode"
                }
            ],
            "barcode_redeem_instructions": "Scan this barcode at the till"
        }),  # account
        json.dumps({
            "transactions_available": True,
            "linking_support": [
                "ADD",
                "REGISTRATION",
                "ENROL"
            ],
            "digital_only": False,
            "has_vouchers": False,
            "authorisation_required": True,
            "card_type": 1,
            "has_points": True,
            "apps": [
                {
                    "app_type": 0
                },
                {
                    "app_type": 1
                }
            ]
        }),  # feature_set
        json.dumps({
            "colour": "#fc03e3",
            "scan_message": "please scan",
            "barcode_type": 0
        }),  # card
        json.dumps([
            {
                "url": "https://api.dev.gb.bink.com/content/dev-media/hermes/schemes/Iceland_dwPpkoM.jpg",
                "id": 372,
                "type": 0,
                "description": "Performance test Hero Image",
                "encoding": "jpg"
            }
        ]),  # images
        json.dumps([{"description": "Placeholder Balance Description", "currency": "GBP", "suffix": ""}]),  # balances
        json.dumps([{"value": "value", "column": "test"}]),  # content
        slug,
    ]


def channel(fixture):
    return [
        fixture['id'],
        fixture['bundle_id']  # bundle_id
    ]


def channel_whitelist(whitelist_id, fixture, plan_id):
    return [
        whitelist_id,  # id
        fixture['id'],  # channel_id
        plan_id,  # membership_plan_id
        fixture["whitelist_status"]  # status
    ]


# TODO: add dynamic service_id and email
def service(fixture, service_id=1, email='performance@test.locust'):
    return [
        service_id,
        f"{email}:{fixture['bundle_id']}",
        fixture['id'],
        json.dumps({
            "email": email,
            "timestamp": 1581597325
        })
    ]


def membership_card(mcard_id='1', membership_plan_id='242', card_number='633174911234560000'):
    add_fields = json.dumps([
        {
            "column": "Card Number",
            "value": card_number
        }
    ], sort_keys=True)
    return [
        mcard_id,  # id
        membership_plan_id,  # membership_plan
        json.dumps({  # status has to be authorised for the pll links to be shown
            "state": "authorised",
            "reason_codes": [
                "X300"
            ]
        }),
        json.dumps({  # card
            "barcode_type": 0,
            "colour": "#f80000"
        }),
        json.dumps([  # images
            {
                "url": "https://api.dev.gb.bink.com/content/dev-media/hermes/schemes/Iceland_dwPpkoM.jpg",
                "id": 372,
                "type": 0,
                "description": "Performance test Hero Image",
                "encoding": "jpg"
            }
        ]),
        add_fields,
        '[]',  # auth fields
        '2020-01-01 00:00:00',  # last status update
        'card_number',  # membership_id
        '[]',  # balances
        '[]',  # vouchers
        '[]',  # membership_transactions
        '[]',  # account
        uuid.uuid4(),  # add_fields_hash
        ''  # auth_fields_hash
    ]


def membership_card_association(association_id, service_id, membership_card_id, plan_whitelist_id):
    return [
        association_id,
        membership_card_id,
        service_id,
        plan_whitelist_id,
        'ACTIVE'
    ]


def payment_card(payment_card_id, fingerprint, token):
    payment_card_id = str(payment_card_id)
    return [
        payment_card_id,  # id
        'ACTIVE',  # status has to be active for the pll links to be shown
        '2020-02-13 15:50:13.879026+00:00',  # status_updated
        fingerprint,  # fingerprint
        json.dumps(False),  # is_deleted
        json.dumps({  # card
            "first_six_digits": f"4{payment_card_id[:5]}",
            "last_four_digits": payment_card_id[:4],
            "month": 11,
            "year": 2022,
            "country": "UK",
            "currency_code": "GBP",
            "name_on_card": "Test Card",
            "provider": "visa",
            "type": "debit"
        }),
        json.dumps({  # account
            "verification_in_progress": False,
            "status": 1,
            "consents": [
                {
                    "type": 1,
                    "timestamp": 1581597325
                }
            ]
        }),
        '[]',  # images
        token,  # token
        uuid.uuid4()  # hash
    ]


def payment_card_association(association_id, service_id, payment_card_id):
    return [
        association_id,
        payment_card_id,
        service_id
    ]


def payment_membership_association(payment_card_id, membership_card_id):
    return [
        payment_card_id,
        membership_card_id
    ]


def all_payment_schemes():
    return [
        [
            "visa",
            json.dumps([{
                "id": 7,
                "type": 0,
                "url": "https://api.dev.gb.bink.com/content/dev-media/hermes/schemes/Visa-Payment_DWQzhta.png",
                "description": "Visa Card Image",
                "encoding": "png"
            }])],
        [
            "mastercard",
            json.dumps([{
                "id": 6,
                "type": 0,
                "url": "https://api.dev.gb.bink.com/content/dev-media/hermes/schemes/Mastercard-Payment_1goHQYv.png",
                "description": "Mastercard Card Image",
                "encoding": "png"
            }])],
        [
            "amex",
            json.dumps([{
                "id": 5,
                "type": 0,
                "url": "https://api.dev.gb.bink.com/content/dev-media/hermes/schemes/Amex-Payment.png",
                "description": "American Express Card Image",
                "encoding": "png"
            }])]
    ]
