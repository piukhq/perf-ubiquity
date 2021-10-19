import json
import uuid

from data_population.fixtures.client import ALL_CLIENTS
from data_population.fixtures.membership_plan import CONSENT_LABEL

PERFORMANCE_CATEGORY_ID = 5000
SENSITIVE_FIELDS = ["Password"]


def category():
    return [
        PERFORMANCE_CATEGORY_ID,  # id
        "performance",  # name
    ]


def membership_plan(scheme_id, name, slug):
    return [
        scheme_id,  # id
        name,  # name
        slug,  # slug
        "https://goo.gl/u72nN9",  # url
        "company",  # company
        "https://goo.gl/xPNXKv",  # company_url
        2,  # tier
        "please scan",  # scan_message
        "pts",  # point_name
        PERFORMANCE_CATEGORY_ID,  # category_id
        "https://www.iceland.co.uk/bonus-card/my-bonus-card/forgotten-password/",  # forgotten_password_url
        "identifier",  # identifier
        True,  # has_transactions
        True,  # has_points
        "#fc03e3",  # colour
        "(.*)",  # barcode_regex
        "(.*)",  # card_number_regex
        "",  # barcode_prefix
        "",  # card_number_prefix
        1,  # barcode_type
        "",  # android_app_id
        "",  # ios_scheme
        "",  # itunes_url
        "",  # play_store_url
        4,  # max_points_value_length
        "https://goo.gl/YzLHX1",  # join_url
        "link account text",  # link_account_text
        "join t and c",  # join_t_and_c
        {"Date", "Reference", "Points"},  # transaction_headers
        True,  # authorisation_required
        True,  # digital_only
        "enrol incentive",  # enrol_incentive
        "plan description",  # plan_description
        "plan name",  # plan_name
        "plan card",  # plan_name_card
        "plan summary",  # plan_summary
        "barcode redeem",  # barcode_redeem_instructions
        "register info",  # plan_register_info
        {"ADD", "REGISTRATION", "ENROL"},  # linking_support
        # False,  # test_scheme,
        json.dumps(
            {
                "0": {
                    "url": "/media/schemes/HarveyNichols_UPPT2Yx.png",
                    "type": 0,
                    "encoding": "png",
                    "description": "performance hero image",
                },
                "8": {},
            }
        ),  # formatted_images
        "#fc03e3",  # secondary_colour
        0,  # plan_popularity
    ]


def card_no_question(question_id, scheme_id):
    return [
        question_id,  # id
        "Card Number",  # label
        scheme_id,  # scheme id
        "card_number",  # type
        0,  # order
        True,  # manual_question
        False,  # scan_question
        False,  # third_party_identifier
        False,  # one_question_link
        2,  # options
        0,  # answer_type
        "NULL",  # choice
        "description",  # description
        "(.*)",  # validation
        True,  # add_field
        False,  # auth_field
        True,  # enrol_field
        False,  # register_field
    ]


def password_question(question_id, scheme_id):
    return [
        question_id,  # id
        "Password",  # label
        scheme_id,  # scheme_id
        "password",  # type
        0,  # order
        False,  # manual_question
        False,  # scan_question
        False,  # third_party_identifier
        False,  # one_question_link
        3,  # options
        1,  # answer_type
        "NULL",  # choice
        "description",  # description
        "(.*)",  # validation
        False,  # add_field
        True,  # auth_field
        True,  # enrol_field
        True,  # register_field
    ]


def scheme_consent(pk, scheme_id):
    return [
        pk,  # id
        True,  # check box
        "performance consent test",  # text
        True,  # is enabled
        False,  # required
        0,  # order
        1,  # journey (link)
        str(uuid.uuid4()),  # slug
        "2020-01-01 00:00:00",  # created on
        "2020-01-01 00:00:00",  # modified on
        scheme_id,  # scheme id
    ]


def third_party_consent_link(pk, client_app_id, scheme_id, scheme_consent_id):
    return [
        pk,  # id
        CONSENT_LABEL,  # consent label
        False,  # add field
        True,  # auth field
        False,  # registration field
        False,  # enrol field
        client_app_id,  # client application id
        scheme_consent_id,  # scheme consent id
        scheme_id,  # scheme id
    ]


def create_all_third_party_consent_links(static_id, consent_id):
    third_party_consent_links = []
    for count in range(len(ALL_CLIENTS)):
        pk = static_id + count
        client = ALL_CLIENTS[count]
        consent_link = third_party_consent_link(pk, client["client_id"], consent_id, consent_id)
        third_party_consent_links.append(consent_link)

    return third_party_consent_links


def scheme_image(pk, scheme_id):
    return [
        pk,  # id
        0,  # image_type_code (hero)
        "",  # size_code
        "",  # strap_line
        "performance hero image",  # description
        "NULL",  # url
        "0",  # call_to_action
        0,  # order
        1,  # status (published)
        "2020-01-01 00:00:00",  # start_date
        "3030-01-01 00:00:00",  # end_date
        "2020-01-01 00:00:00",  # created
        scheme_id,  # scheme
        "schemes/HarveyNichols_UPPT2Yx.png",  # image
        0,  # reward tier
        "png",  # encoding
        "schemes/HarveyNichols_UPPT2Yx.png",  # dark_mode_image
        "NULL",  # dark_mode_url
    ]


def scheme_balance_details(pk, scheme_id):
    return [
        pk,  # id
        "points",  # currency
        "",  # prefix
        "pts",  # suffix
        "Placeholder Balance Description",  # description
        scheme_id,  # scheme id
    ]


def scheme_fee(pk, scheme_id):
    return [
        pk,  # id
        "example fee type",  # fee type
        1.12,  # amount
        scheme_id,  # scheme id
    ]


def scheme_content(pk, scheme_id):
    return [
        pk,  # id
        "performance test",  # column
        "performance test",  # value
        scheme_id,  # scheme id
    ]


def membership_plan_documents(pk, scheme_id):
    return [
        pk,  # id
        "Terms & conditions",  # name
        "I accept the",  # description
        "https://bink.com",  # url
        "{ADD,REGISTRATION,ENROL}",  # display
        True,  # checkbox
        scheme_id,  # scheme id
        0,  # order
    ]


def voucher_scheme(pk, scheme_id):
    return [
        pk,  # id
        "GBP",  # earn_currency
        "£",  # earn_prefix
        "",  # earn_suffix
        "accumulator",  # earn_type
        "GBP",  # burn_currency
        "£",  # burn_prefix
        "",  # burn_suffix
        "voucher",  # burn_type
        "NULL",  # burn_value
        4,  # barcode_type
        "{{earn_target_remaining}} left to go!",  # headline_inprogress
        "Voucher expired",  # headline_expired
        "Voucher redeemed",  # headline_redeemed
        "{{earn_prefix}}{{earn_value}}{{earn_suffix}} voucher earned!",  # headline_issued
        "Performance voucher",  # subtext
        3,  # expiry_months
        scheme_id,  # scheme_id
        "body text expired",  # body_text_expired
        "body text in-progress",  # body_text_inprogress
        "body text issued",  # body_text_issued
        "body text redeemed",  # body_text_redeemed
        "https://bink.com",  # terms_and_conditions_url
        4,  # earn_target_value
        "",  # body_text_cancelled
        "",  # headline_cancelled
    ]
