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
            "registration_fields": [],
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
            "enrol_fields": [],
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
        fixture["status"]  # status
    ]
