import json
import random
import uuid

import arrow

from data_population.fixtures.membership_card import STATIC_MCARD_HISTORY_BODY


def generate_transactions(transaction_total):
    transactions = []
    for count in range(transaction_total):
        transactions.append(
            {
                "date": arrow.now().shift(days=-count).format("DD/MM/YYYY HH:mm:ss"),
                "description": f"Test Transaction: {uuid.uuid4()}",
                "points": str(random.randint(1, 99)),
            }
        )
    return json.dumps(transactions)


def membership_card(card_id, scheme_id, transaction_total):
    card_number = str(uuid.uuid4())
    transactions = generate_transactions(transaction_total)

    return [
        card_id,  # id
        1,  # status
        0,  # order
        "2019-03-12 15:51:36.390742+00",  # created
        "2019-03-15 05:55:28.532571+00",  # updated
        scheme_id,  # scheme_id
        False,  # is_deleted
        "NULL",  # link_date
        "NULL",  # join_date
        json.dumps(
            [
                {
                    "value": 31,
                    "prefix": "",
                    "suffix": "pts",
                    "currency": "points",
                    "updated_at": 1591719196,
                    "description": "Placeholder Balance Description",
                }
            ]
        ),  # balances
        "{}",  # vouchers
        card_number,  # barcode
        card_number,  # card number
        transactions,  # transactions
        card_number,  # main_answer
        json.dumps([]),  # pll_links
        "{}",  # formatted_images
        5,  # originating_journey
    ]


def historical_membership_card(history_id: int) -> list:
    return [
        history_id,  # id
        "2019-03-12 15:51:36.390742+00",  # created
        "create",  # change_type
        history_id,  # instance_id
        "internal_service",  # channel
        history_id,  # user_id
        STATIC_MCARD_HISTORY_BODY,  # body
        "",  # change_details
        "add",  # journey
    ]


def card_number_answer(answer_id, scheme_account_id, question_id):
    return [
        answer_id,  # id
        str(uuid.uuid4()),  # answer
        scheme_account_id,  # scheme_account_id
        question_id,  # question_id
    ]


def password_answer(answer_id, scheme_account_id, question_id):
    return [
        answer_id,  # id
        str(uuid.uuid4()),  # answer
        scheme_account_id,  # scheme_account_id
        question_id,  # question_id
    ]


def transaction(pk, scheme_account_id):
    return [
        pk,  # pk
        scheme_account_id,  # scheme_account_id
        "2019-03-12 15:51:36.390742+00",  # created
        "2019-03-12 15:51:36.390742+00",  # date
        "performance transaction description",  # description
        "performanceland",  # location
        3.0,  # points
        "NULL",  # value
        str(uuid.uuid4()),  # hash
        "NULL",  # user_set
    ]
