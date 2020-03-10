import uuid

from data_population.fixtures import CONSENT_LABEL

PERFORMANCE_CATEGORY_ID = 5000


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
        False,  # test_scheme
    ]


def card_no_question(question_id, scheme_id=105):
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
        3,  # options
        0,  # answer_type
        "\\N",  # choice
        "description",  # description
        "(.*)",  # validation
        True,  # add_field
        False,  # auth_field
        True,  # enrol_field
        True,  # register_field
    ]


def postcode_question(question_id, scheme_id):
    return [
        question_id,  # id
        "Postcode",  # label
        scheme_id,  # scheme_id
        "postcode",  # type
        0,  # order
        False,  # manual_question
        False,  # scan_question
        False,  # third_party_identifier
        False,  # one_question_link
        3,  # options
        0,  # answer_type
        "\\N",  # choice
        "description",  # description
        "(.*)",  # validation
        False,  # add_field
        True,  # auth_field
        True,  # enrol_field
        True,  # register_field
    ]


def service(user_id):
    return [user_id, "", "", "2020-03-09 12:42:15+00"]  # id, latitude, longitude, timestamp


def membership_card(card_id, scheme_id):
    return [
        card_id,  # id
        1,  # status
        0,  # order
        "2019-03-12 15:51:36.390742+00",  # created
        "2019-03-15 05:55:28.532571+00",  # updated
        scheme_id,  # scheme_id
        True,  # is_deleted
        "\\N",  # link_date
        "\\N",  # join_date
        "[{}]",  # balances
        "{}",  # vouchers
    ]


def card_number_answer(answer_id, question_id):
    return [answer_id, uuid.uuid4(), answer_id, question_id]  # id, answer, scheme_account_id, question_id


def postcode_answer(answer_id, scheme_account_id, question_id):
    return [
        answer_id,  # id
        uuid.uuid4(),  # answer
        scheme_account_id,  # scheme_account_id
        question_id,  # question_id
    ]


def payment_card(card_id):
    token = str(uuid.uuid4())
    return [
        card_id,  # id
        "performance test",  # name_on_card
        "\\N",  # start_month
        "\\N",  # start_year
        1,  # expiry_month
        2222,  # expiry_year
        1,  # status
        0,  # order
        "2019-03-12 15:51:36.390742+00",  # created
        "2019-03-15 05:55:28.532571+00",  # updated
        1,  # issuer_id
        1,  # payment_card_id
        str(uuid.uuid4()),  # token
        "UK",  # country
        "GBP",  # currency code
        "3333",  # pan_end
        "333333",  # pan_start
        True,  # is_deleted
        token,  # fingerprint
        token,  # psp_token
        "{}",  # consents
    ]


def card_service_link(user_id):
    return [user_id, user_id, user_id]  # id, scheme_account_id, payment_card_account_id, user_id


def pll_link(user_id):
    return [user_id, True, user_id, user_id]  # id, active_link, payment_card_account_id, scheme_account_id


def organisation(fixture):
    return [fixture['id'], fixture['organisation_name'], "organisation terms and conditions"]


def client_application(fixture):
    return [fixture['client_id'], fixture['client_name'], fixture['id'], fixture['secret']]


def client_application_bundle(fixture):
    return [fixture['id'], fixture['bundle_id'], fixture['client_id']]


def scheme_whitelist(whitelist_id, fixture, scheme_id):
    return [whitelist_id, fixture['status'], fixture['id'], scheme_id]


def consent(pk, scheme_id):
    return [
        pk,  # id
        "Consent text",  # text
        scheme_id,  # scheme id
        True,  # is enabled
        False,  # required
        0,  # order
        1,  # journey (link)
        uuid.uuid4(),  # slug
        True  # check box
    ]


def third_party_consent_link(pk, client_app_id, scheme_id, scheme_consent_id):
    return [
        pk,  # id
        CONSENT_LABEL,  # client label
        client_app_id,  # client application id
        scheme_id,  # scheme id
        scheme_consent_id,  # scheme consent id
        False,  # add field
        True,  # auth field
        False,  # registration field
        False  # enrol field
    ]


def scheme_image(pk, scheme_id):
    return [
        pk,  # id
        0,  # image type code (hero)
        "",  # size code
        "https://performance.sandbox.gb.bink.com/content/dev-media/hermes/schemes/HarveyNichols_UPPT2Yx.png"  # image
        "",  # strap line
        "performance hero image",  # description
        "",  # Url
        "0",  # call to action
        0,  # order
        1,  # status (published)
        "2020-01-01 00:00:00",  # start date
        "3030-01-01 00:00:00",  # end date
        0,  # reward tier
        "",  # encoding
        scheme_id  # scheme
    ]
