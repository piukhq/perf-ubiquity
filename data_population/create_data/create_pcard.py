import uuid

from data_population.fixtures.payment_scheme import PAYMENT_SCHEME_INFO


def issuer(pk, name):
    return [
        pk,  # id
        name,  # name
        "performance/image.jpg"  # image
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
    ]


def create_all_payment_schemes():
    payment_schemes = []
    for slug, scheme_info in PAYMENT_SCHEME_INFO.items():
        row = payment_scheme(
            scheme_info['pk'],
            scheme_info["name"],
            slug,
            scheme_info["url"],
            scheme_info["input_label"],
            scheme_info["system"],
            scheme_info["token_method"]
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
        "NULL",  # encoding
    ]


def create_all_payment_card_images():
    payment_card_images = []
    for scheme_info in PAYMENT_SCHEME_INFO.values():
        row = payment_card_image(
            scheme_info['pk'],
            scheme_info["image"],
            scheme_info['pk']
        )
        payment_card_images.append(row)

    return payment_card_images


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
