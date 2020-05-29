def pll_link(pk, pcard_id, mcard_id):
    return [
        pk,  # id
        True,  # active_link
        pcard_id,  # payment_card_account_id
        mcard_id,  # scheme_account_id
        3,  # vop_link
    ]


def scheme_account(pk, scheme_account_id, user_id):
    return [
        pk,  # id
        scheme_account_id,  # scheme_account_id
        user_id,  # user_id
    ]


def payment_card(pk, payment_card_id, user_id):
    return [
        pk,  # id
        payment_card_id,  # payment_card_account_id
        user_id,  # user_id
    ]
