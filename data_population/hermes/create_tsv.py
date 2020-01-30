import csv
import os
import time
from enum import Enum

from data_population.hermes import create_data
from data_population.fixtures import CLIENT_ONE, CLIENT_TWO, CLIENT_RESTRICTED
from settings import TSV_PATH

LOAD_START_ID = 2000000
STATIC_START_ID = 5000
BULK_SIZE = 1000

CLIENTS = [CLIENT_ONE, CLIENT_TWO, CLIENT_RESTRICTED]
MEMBERSHIP_PLANS = 40
# USERS = 13017000
# MCARDS = 88953620
# PCARDS = 19525500
TOTAL_RECORDS = 100000
USERS = 100
MCARDS = 800
PCARDS = 200


class Files(str, Enum):
    USER = ("users.tsv",)
    SCHEME = ("scheme_scheme.tsv",)
    QUESTION = ("scheme_schemecredentialquestion.tsv",)
    ANSWER = ("scheme_schemeaccountcredentialanswer.tsv",)
    SCHEME_ACCOUNT = ("scheme_schemeaccount.tsv",)
    PAYMENT_ACCOUNT = ("payment_card_paymentcardaccount.tsv",)
    PAYMENT_ACCOUNT_ENTRY = ("ubiquity_paymentcardaccountentry.tsv",)
    SCHEME_ACCOUNT_ENTRY = ("ubiquity_schemeaccountentry.tsv",)
    PAYMENT_SCHEME_ENTRY = ("ubiquity_paymentcardschemeentry.tsv",)
    CONSENT = ("ubiquity_serviceconsent.tsv",)
    ORGANISATION = ("user_organisation.tsv",)
    CLIENT_APP = ("user_clientapplication.tsv",)
    CLIENT_APP_BUNDLE = ("user_clientapplicationbundle.tsv",)
    SCHEME_WHITELIST = ("scheme_schemebundleassociation.tsv",)


def tsv_path(file_name):
    return f"{TSV_PATH}/{file_name}"


def write_to_tsv(file_name, rows):
    path = tsv_path(file_name)
    with open(path, "a") as f:
        tsv_writer = csv.writer(f, delimiter="\t")
        tsv_writer.writerows(rows)


def create_tsv():
    start = time.perf_counter()
    os.makedirs(TSV_PATH, exist_ok=True)
    for file in Files:
        try:
            os.remove(tsv_path(file))
        except FileNotFoundError:
            pass

    organisations = [create_data.organisation(client) for client in CLIENTS]
    write_to_tsv(Files.ORGANISATION, organisations)
    client_applications = [create_data.client_application(client) for client in CLIENTS]
    write_to_tsv(Files.CLIENT_APP, client_applications)
    client_application_bundle = [create_data.client_application_bundle(client) for client in CLIENTS]
    write_to_tsv(Files.CLIENT_APP_BUNDLE, client_application_bundle)

    remaining_membership_plans = MEMBERSHIP_PLANS
    membership_plans = []
    plan_questions = []
    while remaining_membership_plans > 0:
        remaining_membership_plans -= 1
        plan_id = STATIC_START_ID + remaining_membership_plans
        plan_name = f"performance plan {remaining_membership_plans}"
        plan_slug = f"performance-plan-{remaining_membership_plans}"
        membership_plans.append(create_data.membership_plan(plan_id, plan_name, plan_slug))
        plan_questions.append(create_data.card_no_question(plan_id, plan_id))
        plan_questions.append(create_data.postcode_question(plan_id + 1000, plan_id))

    write_to_tsv(Files.SCHEME, membership_plans)
    write_to_tsv(Files.QUESTION, plan_questions)

    whitelist_id = STATIC_START_ID
    whitelist_list = []
    for client_fixture in [CLIENT_ONE, CLIENT_TWO]:
        for plan in membership_plans:
            whitelist_id += 1
            plan_id = plan[0]
            whitelist_list.append(create_data.scheme_whitelist(whitelist_id, client_fixture, plan_id))

    write_to_tsv(Files.SCHEME_WHITELIST, whitelist_list)

    # remaining_services = TOTAL_RECORDS
    # remaining_links = TOTAL_RECORDS
    # remaining_card_no = TOTAL_RECORDS
    # postcode_id = TOTAL_RECORDS * 10
    # while remaining_services > 0:
    #     users = []
    #     services = []
    #     membership_cards = []
    #     payment_cards = []
    #     for _ in range(0, BULK_SIZE):
    #         remaining_services -= 1
    #         user_id = START_ID + remaining_services
    #         # users.append(create_data.user(user_id))
    #         services.append(create_data.service(user_id))
    #         membership_cards.append(create_data.membership_card(user_id))
    #         payment_cards.append(create_data.payment_card(user_id))
    #
    #     write_to_tsv(Files.USER, users)
    #     write_to_tsv(Files.CONSENT, services)
    #     write_to_tsv(Files.PAYMENT_ACCOUNT, payment_cards)
    #     write_to_tsv(Files.SCHEME_ACCOUNT, membership_cards)
    #
    #     manual_answers = []
    #     auth_answers = []
    #     for _ in range(0, BULK_SIZE):
    #         remaining_card_no -= 1
    #         postcode_id -= 1
    #         card_answer_id = START_ID + remaining_card_no
    #         postcode_answer_id = START_ID + postcode_id
    #         manual_answers.append(create_data.card_number_answer(card_answer_id, ))
    #         auth_answers.append(
    #             create_data.postcode_answer(postcode_answer_id, card_answer_id)
    #         )
    #
    #     write_to_tsv(Files.ANSWER, manual_answers)
    #     write_to_tsv(Files.ANSWER, auth_answers)
    #
    #     payment_card_service_links = []
    #     membership_card_service_links = []
    #     pll_links = []
    #     for _ in range(0, BULK_SIZE):
    #         remaining_links -= 1
    #         link_id = START_ID + remaining_links
    #         card_link = create_data.card_service_link(link_id)
    #         payment_card_service_links.append(card_link)
    #         membership_card_service_links.append(card_link)
    #         pll_links.append(create_data.pll_link(link_id))
    #
    #     write_to_tsv(Files.PAYMENT_ACCOUNT_ENTRY, payment_card_service_links)
    #     write_to_tsv(Files.SCHEME_ACCOUNT_ENTRY, membership_card_service_links)
    #     write_to_tsv(Files.PAYMENT_SCHEME_ENTRY, pll_links)
    #     print("Bulk cycle complete.")

    # questions = list()
    # questions.append(create_data.card_no_question())
    # questions.append(create_data.postcode_question())
    # write_to_tsv(Files.QUESTION, questions)

    end = time.perf_counter()
    print(f"Elapsed time: {end - start}")


if __name__ == "__main__":
    create_tsv()
