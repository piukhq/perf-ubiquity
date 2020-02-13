import hashlib
import json


def membership_plan(plan_id, name):
    return [
        plan_id,  # id
        json.dumps({
            "plan_name": name,
            "plan_documents": [
                {
                    "name": "Terms & conditions",
                    "checkbox": True,
                    "url": "url",
                    "display": [
                        "REGISTRATION",
                        "ENROL"
                    ],
                    "description": "Terms & conditions"
                }
            ],
            "company_url": "company-url",
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
        json.dumps([{"value": "value", "column": "test"}])  # content
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
        fixture["daedalus_status"]  # status
    ]


# TODO: add dynamic service_id and email
def service(fixture, service_id=1, email='performance@test.locust'):
    return [
        service_id,
        f"{email}:{fixture['bundle_id']}",
        fixture['id'],
        {
            "email": email,
            "timestamp": 1581597325
        }
    ]


def membership_card(mcard_id, membership_plan_id, card_number=633174911234560000):
    add_fields = json.dumps([
        {
            "column": "Card Number",
            "value": card_number
        }
    ], sort_keys=True)
    return [
        mcard_id,
        membership_plan_id,
        json.dumps({  # status
            "state": "pending",
            "reason_codes": [
                "X100"
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
        hashlib.md5(add_fields.encode()).hexdigest(),  # add_fields hash
        '[]',  # auth fields
        ''  # auth fields hash
    ]


def membership_card_association(association_id, service_id, membership_card_id, plan_whitelist_id):
    return [
        association_id,
        membership_card_id,
        service_id,
        plan_whitelist_id,
        'active'
    ]


def payment_card():
    pass
