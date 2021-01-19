import uuid


def pll_link(pk, pcard_id, mcard_id):
    return [
        pk,  # id
        True,  # active_link
        pcard_id,  # payment_card_account_id
        mcard_id,  # scheme_account_id
    ]

# Not implemented yet
# def historical_pll_link(pll_link, history_id):
#     return [
#         history_id,  # id
#         "2019-03-12 15:51:36.390742+00",  # created
#         "created",  # change_type
#         pll_link[0],  # instance_id
#         "internal_service",  # channel
#         pll_link[2],  # payment_card_account_id
#         pll_link[1],  # scheme_account_id
#         False,  # active_link
#         "",  # change_details
#     ]


def vop_activation(pk, pcard_id, scheme):
    return [
        pk,  # id
        uuid.uuid4(),  # activation_id
        3,  # status
        pcard_id,  # payment_card_account
        scheme,  # scheme
    ]


def scheme_account(pk, scheme_account_id, user_id):
    return [
        pk,  # id
        scheme_account_id,  # scheme_account_id
        user_id,  # user_id
    ]


def historical_scheme_account(scheme_account_entry, history_id):
    return [
        history_id,  # id
        "2019-03-12 15:51:36.390742+00",  # created
        "created",  # change_type
        scheme_account_entry[0],  # instance_id
        "internal_service",  # channel
        scheme_account_entry[2],  # user_id
        scheme_account_entry[1],  # scheme_account_id
        "",  # change_details
    ]


def payment_card(pk, payment_card_id, user_id):
    return [
        pk,  # id
        payment_card_id,  # payment_card_account_id
        user_id,  # user_id
    ]


def historical_payment_card(payment_card_entry, history_id):
    return [
        history_id,  # id
        "2019-03-12 15:51:36.390742+00",  # created
        "created",  # change_type
        payment_card_entry[0],  # instance_id
        "internal_service",  # channel
        payment_card_entry[2],  # user_id
        payment_card_entry[1],  # payment_card_account_id
        "",  # change_details
    ]
