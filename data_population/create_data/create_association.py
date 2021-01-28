import uuid


def pll_link(pk: int, pcard_id: int, mcard_id: int) -> list:
    return [
        pk,  # id
        True,  # active_link
        pcard_id,  # payment_card_account_id
        mcard_id,  # scheme_account_id
    ]


def historical_pll_link(pll_link: list, history_id: int) -> list:
    return [
        history_id,  # id
        "2019-03-12 15:51:36.390742+00",  # created
        "create",  # change_type
        pll_link[0],  # instance_id
        "internal_service",  # channel
        "",  # change_details
        "NULL",  # user_id
        pll_link[2],  # payment_card_account_id
        pll_link[3],  # scheme_account_id
        False,  # active_link
    ]


def vop_activation(pk: int, pcard_id: int, scheme: int) -> list:
    return [
        pk,  # id
        str(uuid.uuid4()),  # activation_id
        3,  # status
        pcard_id,  # payment_card_account
        scheme,  # scheme
    ]


def historical_vop_activation(vop_activation: list, history_id: int) -> list:
    return [
        history_id,  # id
        "2019-03-12 15:51:36.390742+00",  # created
        "create",  # change_type
        vop_activation[0],  # instance_id
        "internal_service",  # channel
        "",  # change_details
        "NULL",  # user_id
        vop_activation[4],  # scheme_id
        vop_activation[3],  # payment_card_account_id
        vop_activation[2],  # status
        vop_activation[1],  # activation_id
    ]


def scheme_account(pk: int, scheme_account_id: int, user_id: int) -> list:
    return [
        pk,  # id
        scheme_account_id,  # scheme_account_id
        user_id,  # user_id
    ]


def historical_scheme_account(scheme_account_entry: list, history_id: int) -> list:
    return [
        history_id,  # id
        "2019-03-12 15:51:36.390742+00",  # created
        "create",  # change_type
        scheme_account_entry[0],  # instance_id
        "internal_service",  # channel
        scheme_account_entry[2],  # user_id
        scheme_account_entry[1],  # scheme_account_id
        "",  # change_details
    ]


def payment_card(pk: int, payment_card_id: int, user_id: int) -> list:
    return [
        pk,  # id
        payment_card_id,  # payment_card_account_id
        user_id,  # user_id
    ]


def historical_payment_card(payment_card_entry: list, history_id: int) -> list:
    return [
        history_id,  # id
        "2019-03-12 15:51:36.390742+00",  # created
        "create",  # change_type
        payment_card_entry[0],  # instance_id
        "internal_service",  # channel
        payment_card_entry[2],  # user_id
        payment_card_entry[1],  # payment_card_account_id
        "",  # change_details
    ]
