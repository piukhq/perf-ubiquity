import json
import uuid


def membership_card(card_id, scheme_id):
    return [
        card_id,  # id
        1,  # status
        0,  # order
        "2019-03-12 15:51:36.390742+00",  # created
        "2019-03-15 05:55:28.532571+00",  # updated
        scheme_id,  # scheme_id
        True,  # is_deleted
        "\\N",  # link_date
        "\\N",  # join_date
        json.dumps([{
            "value": 0.0,
            "points": 380.01,
            "balance": None,
            "is_stale": False,
            "user_set": "",
            "scheme_id": 194,
            "updated_at": 1584012379,
            "reward_tier": 1,
            "value_label": "",
            "points_label": "380",
            "scheme_account_id": card_id
        }]),  # balances
        "{}",  # vouchers
    ]


def card_number_answer(answer_id, scheme_account_id, question_id):
    return [
        answer_id,  # id
        uuid.uuid4(),  # answer
        scheme_account_id,  # scheme_account_id
        question_id  # question_id
    ]


def postcode_answer(answer_id, scheme_account_id, question_id):
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
        "",  # value
        uuid.uuid4(),  # hash
        "",  # user_set
    ]


