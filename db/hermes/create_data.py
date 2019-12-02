import uuid

from settings import SCHEME_ID, BARCLAYS_CLIENT_ID

CARD_NO_QUESTION_ID = 5050
POSTCODE_QUESTION_ID = 5051


def membership_plan():
    return [
        SCHEME_ID,  # id
        "performance test scheme",  # name
        "performance-test",  # slug
        "url",  # url
        "company",  # company
        "company-url",  # company_url
        2,  # tier
        "please scan",  # scan_message
        "pts",  # point_name
        1,  # category_id
        "forgot-url",  # forgotten_password_url
        "identifier",  # identifier
        True,  # has_transactions
        True,  # has_points
        "#fc03e3",  # colour
        "(.*)",  # barcode_regex
        "(.*)",  # card_number_regex
        "",  # barcode_prefix
        "",  # card_number_prefix
        1,  # barcode_type
        "android app id",  # android_app_id
        "ios scheme",  # ios_scheme
        "itunes-url",  # itunes_url
        "play-store-url",  # play_store_url
        4,  # max_points_value_length
        "join-url",  # join_url
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


def card_no_question():
    return [
        CARD_NO_QUESTION_ID,  # id
        "Card Number",  # label
        SCHEME_ID,  # scheme_id
        "card_number",  # type
        0,  # order
        True,  # manual_question
        False,  # scan_question
        False,  # third_party_identifier
        False,  # one_question_link
        1,  # options
        0,  # answer_type
        "\\N",  # choice
        "description",  # description
        "(.*)",  # validation
        True,  # add_field
        False,  # auth_field
        False,  # enrol_field
        False,  # register_field
    ]


def postcode_question():
    return [
        POSTCODE_QUESTION_ID,  # id
        "Postcode",  # label
        SCHEME_ID,  # scheme_id
        "postcode",  # type
        0,  # order
        False,  # manual_question
        False,  # scan_question
        False,  # third_party_identifier
        False,  # one_question_link
        1,  # options
        0,  # answer_type
        "\\N",  # choice
        "description",  # description
        "(.*)",  # validation
        False,  # add_field
        True,  # auth_field
        False,  # enrol_field
        False,  # register_field
    ]


def user(user_id):
    return [
        user_id,  # id
        "LfClBmyjJOtEAodU0VBNXbVa3IbrDXGkPaslMH2cshpF2ZPB34",  # password
        "\\N",  # last_login
        False,  # is_superuser
        "\\N",  # email
        True,  # is_active
        "2019-03-12 15:51:36.390742+00",  # date_joined
        False,  # is_staff
        str(uuid.uuid4()),  # uid
        "\\N",  # facebook
        "\\N",  # twitter
        "\\N",  # reset_token
        "\\N",  # marketing_code_id
        BARCLAYS_CLIENT_ID,  # client_id
        "xTKtQx6e",  # salt
        user_id,  # external_id
        False,  # is_tester
    ]


def service(user_id):
    return [user_id, "\\N", "\\N", "2019-03-07 12:42:15+00"]  # id, latitude, longitude, timestamp


def membership_card(card_id):
    return [
        card_id,  # id
        1,  # status
        0,  # order
        "2019-03-12 15:51:36.390742+00",  # created
        "2019-03-15 05:55:28.532571+00",  # updated
        SCHEME_ID,  # scheme_id
        True,  # is_deleted
        "\\N",  # link_date
        "\\N",  # join_date
        "[{}]",  # balances
        "{}",  # vouchers
    ]


def card_number_answer(answer_id):
    return [answer_id, uuid.uuid4(), answer_id, CARD_NO_QUESTION_ID]  # id, answer, scheme_account_id, question_id


def postcode_answer(answer_id, scheme_account_id):
    return [
        answer_id,  # id
        uuid.uuid4(),  # answer
        scheme_account_id,  # scheme_account_id
        POSTCODE_QUESTION_ID,  # question_id
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
