import json

from request_data.membership_plan import PlanIDs, ClientIDs


def membership_plan():
    return [
        PlanIDs.TEST_SCHEME_ID.value,  # id
        json.dumps({
            "plan_name": "performance test scheme",
            "plan_documents": [
                {
                    "name": "Terms & conditions",
                    "checkbox": True,
                    "url": "https://policies.bink.com/iceland/tc.html",
                    "display": [
                        "REGISTRATION",
                        "ENROL"
                    ],
                    "description": "Terms & conditions"
                },
                {
                    "name": "Privacy Policy",
                    "checkbox": True,
                    "url": "https://policies.bink.com/iceland/pp.html",
                    "display": [
                        "REGISTRATION",
                        "ENROL"
                    ],
                    "description": "Privacy Policy"
                }
            ],
            "company_url": "https://goo.gl/xPNXKv",
            "plan_description": "Test plan description",
            "tiers": [],
            "plan_name_card": "Performance Test",
            "fees": [
                {
                    "type": "enrolment",
                    "amount": 1.1
                }
            ],
            "enrol_incentive": "Placeholder Enrol Incentive",
            "category": "Household",
            "company_name": "Performance test",
            "plan_register_info": "Registrations typically processed in 24hrs",
            "plan_summary": "Test plan summary",
            "add_fields": [
                {
                    "choice": [],
                    "validation": "(.*)",
                    "column": "Card Number",
                    "type": 0,
                    "common_name": "card_number"
                }
            ],
            "authorise_fields": [
                {
                    "choice": [],
                    "validation": "(.*)",
                    "column": "Postcode",
                    "type": 0,
                    "common_name": "postcode"
                }
            ],
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
            "colour": "#f80000",
            "scan_message": "Please turn over to scan barcode",
            "barcode_type": 0
        }),  # card
        json.dumps([
            {
                "url": "https://api.dev.gb.bink.com/content/dev-media/hermes/schemes/iceland-asset.png",
                "id": 373,
                "type": 4,
                "description": "",
                "encoding": "png"
            },
            {
                "url": "https://api.dev.gb.bink.com/content/dev-media/hermes/schemes/Iceland_dwPpkoM.jpg",
                "id": 372,
                "type": 0,
                "description": "Performance test Hero Image",
                "encoding": "jpg"
            },
            {
                "url": "https://api.dev.gb.bink.com/content/dev-media/hermes/schemes/Iceland-icon4.png",
                "id": 374,
                "type": 3,
                "description": "Performance test Icon",
                "encoding": "png"
            },
            {
                "url": "https://api.dev.gb.bink.com/content/dev-media/hermes/schemes/Tier-4-a_copy_B9FdOEH.png",
                "id": 540,
                "type": 2,
                "description": "Tier-4-barcode_tile",
                "encoding": "png"
            },
            {
                "url": "https://api.dev.gb.bink.com/content/dev-media/hermes/schemes/iceland_ref3.jpg",
                "id": 521,
                "type": 5,
                "description": "Performance test Reference",
                "encoding": "jpg"
            },
            {
                "url": "https://api.dev.gb.bink.com/content/dev-media/hermes/schemes/iceland-300x197.jpg",
                "id": 545,
                "type": 1,
                "description": "Performance test Test Banner",
                "encoding": "jpg"
            },
            {
                "url": "https://api.dev.gb.bink.com/content/dev-media/hermes/schemes/iceland-300x197_pxucuAx.jpg",
                "id": 546,
                "type": 6,
                "description": "Performance test Test Personal Offer",
                "encoding": "jpg"
            },
            {
                "url": "https://api.dev.gb.bink.com/content/dev-media/hermes/schemes/iceland-300x197_jQohtHm.jpg",
                "id": 547,
                "type": 7,
                "description": "Performance test Test Promo",
                "encoding": "jpg"
            }
        ]),  # images
        json.dumps([{"description": "Placeholder Balance Description", "currency": "GBP", "suffix": ""}]),  # balances
        json.dumps([{"value": "value", "column": "test"}])  # content
    ]


def channel_whitelist():
    return [
        5050,  # id
        ClientIDs.BARCLAYS.value,  # channel_id
        PlanIDs.TEST_SCHEME_ID.value,  # membership_plan_id
        "ACTIVE"  # status
    ]
