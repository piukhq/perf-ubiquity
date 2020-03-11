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
        "[{}]",  # balances
        "{}",  # vouchers
    ]


def card_number_answer(answer_id, question_id):
    return [answer_id, uuid.uuid4(), answer_id, question_id]  # id, answer, scheme_account_id, question_id


def postcode_answer(answer_id, scheme_account_id, question_id):
    return [
        answer_id,  # id
        uuid.uuid4(),  # answer
        scheme_account_id,  # scheme_account_id
        question_id,  # question_id
    ]