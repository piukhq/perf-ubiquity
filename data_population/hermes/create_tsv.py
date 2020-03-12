import csv
import os
import random
import time
from enum import Enum

from data_population.fixtures import ALL_CLIENTS, NON_RESTRICTED_CLIENTS, ALL_PAYMENT_PROVIDER_STATUS_MAPPINGS
from data_population.hermes.create_data import (create_channel, create_plan, create_pcard, create_mcard,
                                                create_service, create_association)

TSV_PATH = f"{os.path.dirname(__file__)}/tsv"
BULK_SIZE = 1000

MEMBERSHIP_PLANS = 100
# USERS = 13017000
# MCARDS = 88953620
# PCARDS = 19525500
TOTAL_SERVICES = 100
TOTAL_MCARDS = 800
TOTAL_PCARDS = 200
TOTAL_TRANSACTIONS = 100

MCARDS_PER_SERVICE = 7
PCARDS_PER_SERVICE = 2


class Files(str, Enum):
    ORGANISATION = "user_organisation.tsv"
    CLIENT_APP = "user_clientapplication.tsv"
    CLIENT_APP_BUNDLE = "user_clientapplicationbundle.tsv"
    CATEGORY = "scheme_catagory.tsv"
    SCHEME = "scheme_scheme.tsv"
    SCHEME_BALANCE_DETAILS = "scheme_schemebalancedetails.tsv"
    SCHEME_FEE = "scheme_schemefee.tsv"
    SCHEME_CONTENT = "scheme_schemecontent.tsv"
    QUESTION = "scheme_schemecredentialquestion.tsv"
    SCHEME_CONSENT = "scheme_schemeconsent.tsv"
    THIRD_PARTY_CONSENT_LINK = "scheme_schemethirdpartyconsentlink.tsv"
    SCHEME_IMAGE = "scheme_schemeimage.tsv"
    SCHEME_WHITELIST = "scheme_schemebundleassociation.tsv"
    VOUCHER_SCHEME = "scheme_voucherscheme.tsv"
    MEMBERSHIP_PLAN_DOCUMENTS = "ubiquity_membershipplandocument"
    PAYMENT_SCHEME = "payment_card_paymentcard.tsv"
    PAYMENT_CARD_IMAGE = "payment_card_paymentcardimage.tsv"
    PROVIDER_STATUS_MAPPING = "payment_card_providerstatusmapping"
    USER = "users.tsv"
    CONSENT = "ubiquity_serviceconsent.tsv"
    SCHEME_ACCOUNT = "scheme_schemeaccount.tsv"
    ANSWER = "scheme_schemeaccountcredentialanswer.tsv"
    PAYMENT_ACCOUNT = "payment_card_paymentcardaccount.tsv"
    PAYMENT_ACCOUNT_ENTRY = "ubiquity_paymentcardaccountentry.tsv"
    SCHEME_ACCOUNT_ENTRY = "ubiquity_schemeaccountentry.tsv"
    PAYMENT_SCHEME_ENTRY = "ubiquity_paymentcardaccountentry.tsv"
    PAYMENT_MEMBERSHIP_ENTRY = "ubiquity_paymentcardschemeentry.tsv"
    # transactions are stored in hades so need to be uploaded to the hades database
    TRANSACTIONS = "transaction.tsv"


def tsv_path(file_name):
    return f"{TSV_PATH}/{file_name}"


def write_to_tsv(file_name, rows):
    path = tsv_path(file_name)
    with open(path, "a") as f:
        tsv_writer = csv.writer(f, delimiter="\t")
        tsv_writer.writerows(rows)


def delete_old_tsv_files():
    os.makedirs(TSV_PATH, exist_ok=True)
    for file in Files:
        try:
            os.remove(tsv_path(file))
        except FileNotFoundError:
            pass


def create_channel_tsv_files():
    organisations = [create_channel.organisation(client) for client in ALL_CLIENTS]
    write_to_tsv(Files.ORGANISATION, organisations)
    client_applications = [create_channel.client_application(client) for client in ALL_CLIENTS]
    write_to_tsv(Files.CLIENT_APP, client_applications)
    client_application_bundle = [create_channel.client_application_bundle(client) for client in ALL_CLIENTS]
    write_to_tsv(Files.CLIENT_APP_BUNDLE, client_application_bundle)


def create_payment_scheme_tsv_files():
    payment_schemes = create_pcard.create_all_payment_schemes()
    write_to_tsv(Files.PAYMENT_SCHEME, payment_schemes)
    payment_images = create_pcard.create_all_payment_card_images()
    write_to_tsv(Files.PAYMENT_CARD_IMAGE, payment_images)
    write_to_tsv(Files.PROVIDER_STATUS_MAPPING, ALL_PAYMENT_PROVIDER_STATUS_MAPPINGS)


def create_membership_plan_tsv_files():
    categories = [create_plan.category()]
    write_to_tsv(Files.CATEGORY, categories)

    membership_plans = []
    plan_questions = []
    scheme_images = []
    scheme_balance_details = []
    scheme_contents = []
    membership_plan_documents = []
    scheme_consents = []
    third_party_consents = []
    voucher_schemes = []
    for count in range(0, MEMBERSHIP_PLANS):
        plan_name = f"performance plan {count}"
        plan_slug = f"performance-plan-{count}"
        membership_plans.append(create_plan.membership_plan(count, plan_name, plan_slug))
        plan_questions.append(create_plan.card_no_question(count, count))
        postcode_question_id = MEMBERSHIP_PLANS + count
        plan_questions.append(create_plan.postcode_question(postcode_question_id, count))
        scheme_images.append(create_plan.scheme_image(count, count))
        scheme_balance_details.append(create_plan.scheme_balance_details(count, count))
        scheme_contents.append(create_plan.scheme_content(count, count))
        membership_plan_documents.append(create_plan.membership_plan_documents(count, count))
        scheme_consent = create_plan.scheme_consent(count, count)
        scheme_consents.append(scheme_consent)
        plan_third_party_consent_links = create_plan.create_all_third_party_consent_links(count)
        third_party_consents.extend(plan_third_party_consent_links)
        if count == 0:
            voucher_schemes.append(create_plan.voucher_scheme(count, count))

    write_to_tsv(Files.SCHEME, membership_plans)
    write_to_tsv(Files.QUESTION, plan_questions)
    write_to_tsv(Files.SCHEME_IMAGE, scheme_images)
    write_to_tsv(Files.SCHEME_BALANCE_DETAILS, scheme_balance_details)
    write_to_tsv(Files.SCHEME_CONTENT, scheme_contents)
    write_to_tsv(Files.MEMBERSHIP_PLAN_DOCUMENTS, membership_plan_documents)
    write_to_tsv(Files.SCHEME_CONSENT, scheme_consents)
    write_to_tsv(Files.THIRD_PARTY_CONSENT_LINK, third_party_consents)
    write_to_tsv(Files.VOUCHER_SCHEME, voucher_schemes)

    whitelist_list = []
    whitelist_id = 0
    for client_fixture in NON_RESTRICTED_CLIENTS:
        for plan in membership_plans:
            whitelist_id += 1
            plan_id = plan[0]
            whitelist_list.append(create_channel.channel_scheme_whitelist(whitelist_id, client_fixture, plan_id))

    write_to_tsv(Files.SCHEME_WHITELIST, whitelist_list)


def create_load_data_tsv_files():
    remaining_services = TOTAL_SERVICES
    remaining_mcards = TOTAL_MCARDS
    remaining_pcards = TOTAL_PCARDS
    users = []
    services = []
    membership_cards = []
    membership_card_associations = []
    payment_cards = []
    payment_card_associations = []

    while remaining_services > 0:
        users = []
        services = []
        membership_cards = []
        membership_card_associations = []
        payment_cards = []
        payment_card_associations = []
        pll_links = []
        for _ in range(0, BULK_SIZE):
            remaining_services -= 1
            service_pk = remaining_services
            users.append(create_service.user(service_pk))
            services.append(create_service.service(service_pk))
            for _ in range(0, MCARDS_PER_SERVICE):
                remaining_mcards -= 1
                if remaining_mcards > 0:
                    scheme_id = random.randint(0, MEMBERSHIP_PLANS)
                    membership_cards.append(create_mcard.membership_card(remaining_mcards, scheme_id))
                    membership_card_associations.append(
                        create_association.scheme_account(remaining_mcards, remaining_mcards, service_pk)
                    )
            for _ in range(0, PCARDS_PER_SERVICE):
                remaining_pcards -= 1
                if remaining_pcards > 0:
                    payment_cards.append(create_pcard.payment_card(remaining_pcards))
                    payment_card_associations.append(
                        create_association.payment_card(remaining_pcards, remaining_pcards, service_pk)
                    )
            pll_links.append(
                create_association.pll_link(remaining_pcards + 1, remaining_pcards + 1, remaining_mcards + 1)
            )

        write_to_tsv(Files.USER, users)
        write_to_tsv(Files.CONSENT, services)
        write_to_tsv(Files.SCHEME_ACCOUNT, membership_cards)
        write_to_tsv(Files.SCHEME_ACCOUNT_ENTRY, membership_card_associations)
        write_to_tsv(Files.PAYMENT_ACCOUNT, payment_cards)
        write_to_tsv(Files.PAYMENT_ACCOUNT_ENTRY, payment_card_associations)
        write_to_tsv(Files.PAYMENT_MEMBERSHIP_ENTRY, membership_card_associations)

    while remaining_mcards > 0:
        membership_cards = []
        for _ in range(0, BULK_SIZE):
            remaining_mcards -= 1
            if remaining_mcards > 0:
                scheme_id = random.randint(0, MEMBERSHIP_PLANS)
                membership_cards.append(create_mcard.membership_card(remaining_mcards, scheme_id))

        write_to_tsv(Files.SCHEME_ACCOUNT, membership_cards)

    while remaining_pcards > 0:
        payment_cards = []
        for _ in range(0, BULK_SIZE):
            payment_cards -= 1
            if remaining_pcards > 0:
                payment_cards.append(create_pcard.payment_card(remaining_pcards))

    add_answers = []
    auth_answers = []
    remaining_answers = TOTAL_MCARDS
    while remaining_answers > 0:
        for _ in range(0, BULK_SIZE):
            remaining_answers -= 1
            add_answer_pk = remaining_answers
            add_question_pk = random.randint(0, MEMBERSHIP_PLANS)
            add_answers.append(create_mcard.card_number_answer(add_answer_pk, remaining_answers, add_question_pk))
            auth_answer_pk = TOTAL_MCARDS + remaining_answers
            auth_question_pk = add_question_pk + 1
            auth_answers.append(create_mcard.postcode_answer(auth_answer_pk, remaining_answers, auth_question_pk))

        write_to_tsv(Files.ANSWER, add_answers)
        write_to_tsv(Files.ANSWER, auth_answers)


def create_transaction_tsv_files():
    remaining_transactions = TOTAL_TRANSACTIONS
    while remaining_transactions > 0:
        transactions = []
        for _ in range(0, BULK_SIZE):
            if remaining_transactions <= 0:
                break
            remaining_transactions -= 1
            transactions.append(create_mcard.transaction(remaining_transactions, remaining_transactions))

        write_to_tsv(Files.TRANSACTIONS, transactions)


if __name__ == "__main__":
    start = time.perf_counter()
    delete_old_tsv_files()
    create_channel_tsv_files()
    create_payment_scheme_tsv_files()
    create_membership_plan_tsv_files()
    create_load_data_tsv_files()
    create_transaction_tsv_files()
    end = time.perf_counter()
    print(f"Elapsed time: {end - start}")
