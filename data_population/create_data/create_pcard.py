import json
import uuid

from data_population.fixtures.payment_scheme import PAYMENT_SCHEME_INFO


def issuer(pk, name):
    return [
        pk,  # id
        name,  # name
        "performance/image.jpg",  # image
    ]


def payment_scheme(pk, name, slug, url, input_label, system, token_method):
    return [
        pk,  # id
        name,  # name
        slug,  # slug
        url,  # url
        "example scan message",  # scan message
        input_label,  # input label
        True,  # is active
        system,  # system
        "debit",  # type
        token_method,  # token_method
        "{}",  # formatted_images
    ]


def create_all_payment_schemes():
    payment_schemes = []
    for slug, scheme_info in PAYMENT_SCHEME_INFO.items():
        row = payment_scheme(
            scheme_info["pk"],
            scheme_info["name"],
            slug,
            scheme_info["url"],
            scheme_info["input_label"],
            scheme_info["system"],
            scheme_info["token_method"],
        )
        payment_schemes.append(row)

    return payment_schemes


def payment_card_image(pk, image, payment_scheme_id):
    return [
        pk,  # id
        0,  # image_type_code (hero)
        "",  # size_code
        image,  # image
        "",  # strap_line
        "performance payment image",  # description
        "NULL",  # url
        "0",  # call_to_action
        0,  # order
        1,  # status (published)
        "2020-01-01 00:00:00",  # start_date
        "3030-01-01 00:00:00",  # end_date
        "2020-01-01 00:00:00",  # created
        payment_scheme_id,  # scheme
        0,  # reward_tier
        "NULL",  # encoding,
        image,  # dark_mode_image
        "NULL",  # dark_mode_url
    ]


def create_all_payment_card_images():
    payment_card_images = []
    for scheme_info in PAYMENT_SCHEME_INFO.values():
        row = payment_card_image(scheme_info["pk"], scheme_info["image"], scheme_info["pk"])
        payment_card_images.append(row)

    return payment_card_images


def payment_card_account_image(pk, image_type_code):
    account_image_scheme = PAYMENT_SCHEME_INFO["mastercard"]

    return [
        pk,  # id
        image_type_code,  # image_type_code
        "",  # size_code
        account_image_scheme["image"],  # image
        "",  # strap_line
        "barclays",  # description
        "NULL",  # url
        "0",  # call_to_action
        0,  # order
        "2020-01-01 00:00:00",  # created
        "3030-01-01 00:00:00",  # end_date
        "NULL",  # payment_card_id
        "2020-01-01 00:00:00",  # start_date
        1,  # status (published)
        0,  # reward_tier
        "NULL",  # encoding
        account_image_scheme["image"],  # dark_mode_image
        "NULL",  # dark_mode_url
    ]


def create_all_payment_card_account_images():
    payment_card_account_images = []
    for count, image_type_code in enumerate([0, 6]):
        row = payment_card_account_image(count + 1, image_type_code)
        payment_card_account_images.append(row)

    return payment_card_account_images


def payment_card(card_id):
    token = str(uuid.uuid4())
    return [
        card_id,  # id
        "performance test",  # name_on_card
        "NULL",  # start_month
        "NULL",  # start_year
        1,  # expiry_month
        2222,  # expiry_year
        1,  # status
        0,  # order
        "2019-03-12 15:51:36.390742+00",  # created
        "2019-03-15 05:55:28.532571+00",  # updated
        1,  # issuer_id
        1,  # payment_card_id
        token,  # token
        "UK",  # country
        "GBP",  # currency code
        "3333",  # pan_end
        "333333",  # pan_start
        False,  # is_deleted
        token,  # fingerprint
        token,  # psp_token
        "{}",  # consents
        token,  # hash
        "{}",  # formatted_images
        json.dumps([]),  # PLL_links
    ]


def historical_payment_card(p_card: list, history_id: int) -> list:
    return [
        p_card[0],  # id
        p_card[1],  # name_on_card
        p_card[2],  # start_month
        p_card[3],  # start_year
        p_card[4],  # expiry_month
        p_card[5],  # expiry_year
        p_card[14],  # currency code
        p_card[13],  # country
        p_card[12],  # token
        p_card[19],  # psp_token
        p_card[16],  # pan_start
        p_card[15],  # pan_end
        p_card[6],  # status
        p_card[7],  # order
        p_card[8],  # created
        p_card[9],  # updated
        p_card[18],  # fingerprint
        p_card[17],  # is_deleted
        p_card[20],  # consents
        p_card[21],  # hash
        p_card[22],  # formatted_images
        p_card[23],  # PLL_links
        history_id,
        "2019-03-12 15:51:36.390742+00",  # history_date
        "NULL",  # history_change_reason
        "~",  # history_type ~ == update
        "NULL",  # history_user_id,
        p_card[10],  # issuer id
        p_card[11],  # payment card id
    ]
