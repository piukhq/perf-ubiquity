import uuid


def pll_link(pk, pcard_id, mcard_id):
    return [
        pk,  # id
        True,  # active_link
        pcard_id,  # payment_card_account_id
        mcard_id,  # scheme_account_id
    ]


def historical_pll_link(pll_link, history_id):
    return [
        pll_link[0],  # id
        False,  # active_link
        history_id,
        "2019-03-12 15:51:36.390742+00",  # history_date
        "NULL",  # history_change_reason
        "~",  # history_type ~ == update
        "NULL",  # history_user_id
        pll_link[2],  # payment_card_account_id
        pll_link[3],  # scheme_account_id
    ]


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


def historical_scheme_account(scheme_account, history_id):
    return [
        scheme_account[0],  # id
        history_id,
        "2019-03-12 15:51:36.390742+00",  # history_date
        "NULL",  # history_change_reason
        "+",  # history_type + == create
        "NULL",  # history_user_id
        scheme_account[1],  # scheme_account_id
        scheme_account[2],  # user_id
    ]


def payment_card(pk, payment_card_id, user_id):
    return [
        pk,  # id
        payment_card_id,  # payment_card_account_id
        user_id,  # user_id
    ]


def historical_payment_card(payment_card, history_id):
    return [
        payment_card[0],  # id
        history_id,
        "2019-03-12 15:51:36.390742+00",  # history_date
        "NULL",  # history_change_reason
        "+",  # history_type + == create
        "NULL",  # history_user_id
        payment_card[1],  # payment_card_account_id
        payment_card[2],  # user_id
    ]
