import json
import random
import uuid

import arrow

from data_population.fixtures.payment_card import STATIC_PCARD_HISTORY_BODY
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
    pcard_id_list = list(range(1, len(PAYMENT_SCHEME_INFO) + 1))
    payment_card_id = random.choices(pcard_id_list, weights=[1, 4, 5], k=1)
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
        payment_card_id,  # payment_card_id
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
        "{}",  # agent_data
        "",  # card_nickname
        "",  # issuer_name
    ]


def historical_payment_card(history_id: int) -> list:
    return [
        history_id,  # id
        "2019-03-12 15:51:36.390742+00",  # created
        "create",  # change_type
        history_id,  # instance_id
        "internal_service",  # channel
        history_id,  # user_id
        STATIC_PCARD_HISTORY_BODY,  # body
        "",  # change_details
        arrow.now(),  # event_time
    ]
