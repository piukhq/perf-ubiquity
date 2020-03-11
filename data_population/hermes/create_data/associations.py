def card_service_link(user_id):
    return [user_id, user_id, user_id]  # id, scheme_account_id, payment_card_account_id, user_id


def pll_link(user_id):
    return [user_id, True, user_id, user_id]  # id, active_link, payment_card_account_id, scheme_account_id