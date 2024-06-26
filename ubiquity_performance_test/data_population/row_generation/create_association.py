import uuid

import arrow


def pll_link(pk: int, pcard_id: int, mcard_id: int) -> list:
    return [
        pk,  # id
        True,  # active_link
        pcard_id,  # payment_card_account_id
        mcard_id,  # scheme_account_id
    ]


def pll_user_association(pk: int, pll_id: int, user_id: int) -> list:
    return [
        pk,  # id
        1,  # state
        "",  # slug
        "2019-03-12 15:51:36.390742+00",  # created
        "2019-03-15 05:55:28.532571+00",  # updated
        pll_id,  # pll_id
        user_id,  # user_id
    ]


def historical_pll_link(history_id: int) -> list:
    return [
        history_id,  # id
        "2019-03-12 15:51:36.390742+00",  # created
        "create",  # change_type
        history_id,  # instance_id
        "internal_service",  # channel
        "",  # change_details
        "NULL",  # user_id
        history_id,  # scheme_account_id
        history_id,  # payment_card_account_id
        False,  # active_link
        arrow.now(),  # event_time
    ]


def vop_activation(pk: int, pcard_id: int, scheme: int) -> list:
    return [
        pk,  # id
        str(uuid.uuid4()),  # activation_id
        3,  # status
        pcard_id,  # payment_card_account
        scheme,  # scheme
    ]


def historical_vop_activation(history_id: int) -> list:
    return [
        history_id,  # id
        "2019-03-12 15:51:36.390742+00",  # created
        "create",  # change_type
        history_id,  # instance_id
        "internal_service",  # channel
        "",  # change_details
        "NULL",  # user_id
        history_id,  # scheme_id
        history_id,  # payment_card_account_id
        history_id,  # status
        history_id,  # activation_id
        arrow.now(),  # event_time
    ]


def scheme_account(pk: int, scheme_account_id: int, user_id: int) -> list:
    return [
        pk,  # id
        scheme_account_id,  # scheme_account_id
        user_id,  # user_id
        1,  # link_status
        True,  # authorise
    ]


def historical_scheme_account(history_id: int) -> list:
    return [
        history_id,  # id
        "2019-03-12 15:51:36.390742+00",  # created
        "create",  # change_type
        history_id,  # instance_id
        "internal_service",  # channel
        history_id,  # user_id
        history_id,  # scheme_account_id
        "",  # change_details
        arrow.now(),  # event_time
        1,  # link_status
    ]


def payment_card(pk: int, payment_card_id: int, user_id: int) -> list:
    return [
        pk,  # id
        payment_card_id,  # payment_card_account_id
        user_id,  # user_id
    ]


def historical_payment_card(history_id: int) -> list:
    return [
        history_id,  # id
        "2019-03-12 15:51:36.390742+00",  # created
        "create",  # change_type
        history_id,  # instance_id
        "internal_service",  # channel
        history_id,  # user_id
        history_id,  # payment_card_account_id
        "",  # change_details
        arrow.now(),  # event_time
    ]
