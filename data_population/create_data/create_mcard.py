import json
import random
import uuid

import arrow


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
    card_number = uuid.uuid4()
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
    ]


def historical_membership_card(original_m_card: list, history_id: int) -> list:
    m_card = original_m_card.copy()
    scheme_id = m_card.pop(5)
    return [
        *m_card,
        history_id,
        "2019-03-12 15:51:36.390742+00",  # history_date
        "NULL",  # history_change_reason
        "~",  # history_type ~ == update
        "NULL",  # history_user_id,
        scheme_id
    ]


def card_number_answer(answer_id, scheme_account_id, question_id):
    return [
        answer_id,  # id
        uuid.uuid4(),  # answer
        scheme_account_id,  # scheme_account_id
        question_id,  # question_id
    ]


def password_answer(answer_id, scheme_account_id, question_id):
    return [
        answer_id,  # id
        uuid.uuid4(),  # answer
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
        uuid.uuid4(),  # hash
        "NULL",  # user_set
    ]
