def card_service_link(static_id):
    return [
        static_id,  # id
        static_id,  # scheme_account_id
        static_id,  # payment_card_account_id
        static_id  # user_id
    ]


def pll_link(user_id):
    return [
        user_id,  # id
        True,  # active_link
        user_id,  # payment_card_account_id
        user_id  # scheme_account_id
    ]
