import csv
import os
import time
from enum import Enum

from db.hermes import create_data
from settings import TSV_PATH

START_ID = 2000000
TOTAL_RECORDS = 10000
BULK_SIZE = 1000


class Files(str, Enum):
    USER = 'users.tsv',
    SCHEME = 'scheme_scheme.tsv',
    QUESTION = 'scheme_schemecredentialquestion.tsv',
    ANSWER = 'scheme_schemeaccountcredentialanswer.tsv',
    SCHEME_ACCOUNT = 'scheme_schemeaccount.tsv',
    PAYMENT_ACCOUNT = 'payment_card_paymentcardaccount.tsv',
    PAYMENT_ACCOUNT_ENTRY = 'ubiquity_paymentcardaccountentry.tsv',
    SCHEME_ACCOUNT_ENTRY = 'ubiquity_schemeaccountentry.tsv',
    PAYMENT_SCHEME_ENTRY = 'ubiquity_paymentcardschemeentry.tsv',
    CONSENT = 'ubiquity_serviceconsent.tsv',
    CLIENT_APP = 'scheme_scheme.tsv',
    ORGANISATION = 'scheme_scheme.tsv',


def tsv_path(file_name):
    return f"{TSV_PATH}/{file_name}"


def write_to_tsv(file_name, rows):
    path = tsv_path(file_name)
    with open(path, 'a') as f:
        tsv_writer = csv.writer(f, delimiter='\t')
        tsv_writer.writerows(rows)


def create_tsv():
    start = time.perf_counter()
    os.makedirs(TSV_PATH, exist_ok=True)
    for file in Files:
        try:
            os.remove(tsv_path(file))
        except FileNotFoundError:
            pass

    remaining_services = TOTAL_RECORDS
    remaining_links = TOTAL_RECORDS
    remaining_card_no = TOTAL_RECORDS
    postcode_id = TOTAL_RECORDS * 10
    while remaining_services > 0:
        users = []
        services = []
        membership_cards = []
        payment_cards = []
        for _ in range(0, BULK_SIZE):
            remaining_services -= 1
            user_id = START_ID + remaining_services
            users.append(create_data.user(user_id))
            services.append(create_data.service(user_id))
            membership_cards.append(create_data.membership_card(user_id))
            payment_cards.append(create_data.payment_card(user_id))

        write_to_tsv(Files.USER, users)
        write_to_tsv(Files.CONSENT, services)
        write_to_tsv(Files.PAYMENT_ACCOUNT, payment_cards)
        write_to_tsv(Files.SCHEME_ACCOUNT, membership_cards)

        manual_answers = []
        auth_answers = []
        for _ in range(0, BULK_SIZE):
            remaining_card_no -= 1
            postcode_id -= 1
            card_answer_id = START_ID + remaining_card_no
            postcode_answer_id = START_ID + postcode_id
            manual_answers.append(create_data.card_number_answer(card_answer_id))
            auth_answers.append(create_data.postcode_answer(postcode_answer_id, card_answer_id))

        write_to_tsv(Files.ANSWER, manual_answers)
        write_to_tsv(Files.ANSWER, auth_answers)

        payment_card_service_links = []
        membership_card_service_links = []
        pll_links = []
        for _ in range(0, BULK_SIZE):
            remaining_links -= 1
            link_id = START_ID + remaining_links
            card_link = create_data.card_service_link(link_id)
            payment_card_service_links.append(card_link)
            membership_card_service_links.append(card_link)
            pll_links.append(create_data.pll_link(link_id))

        write_to_tsv(Files.PAYMENT_ACCOUNT_ENTRY, payment_card_service_links)
        write_to_tsv(Files.SCHEME_ACCOUNT_ENTRY, membership_card_service_links)
        write_to_tsv(Files.PAYMENT_SCHEME_ENTRY, pll_links)
        print("Bulk cycle complete.")

    print("Creating scheme data...")
    schemes = [create_data.membership_plan()]
    write_to_tsv(Files.SCHEME, schemes)

    questions = list()
    questions.append(create_data.card_no_question())
    questions.append(create_data.postcode_question())
    write_to_tsv(Files.QUESTION, questions)

    end = time.perf_counter()
    print(f"Elapsed time: {end - start}")


if __name__ == "__main__":
    create_tsv()
