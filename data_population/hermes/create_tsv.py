import csv
import os
import time
from enum import Enum

from data_population.fixtures import ALL_CLIENTS, NON_RESTRICTED_CLIENTS
from data_population.hermes.create_data import create_channel, create_plan


TSV_PATH = f"{os.path.dirname(__file__)}/tsv"
LOAD_START_ID = 2000000
STATIC_START_ID = 5000
BULK_SIZE = 1000

MEMBERSHIP_PLANS = 100
# USERS = 13017000
# MCARDS = 88953620
# PCARDS = 19525500
TOTAL_RECORDS = 100000
USERS = 100
MCARDS = 800
PCARDS = 200


class Files(str, Enum):
    ORGANISATION = "user_organisation.tsv"
    CLIENT_APP = "user_clientapplication.tsv"
    CLIENT_APP_BUNDLE = "user_clientapplicationbundle.tsv"
    CATEGORY = "scheme_catagory.tsv"
    SCHEME = "scheme_scheme.tsv"
    # Scheme balance details
    # Scheme fees
    # Scheme content
    QUESTION = "scheme_schemecredentialquestion.tsv"
    SCHEME_CONSENT = "scheme_schemeconsent.tsv"
    THIRD_PARTY_CONSENT_LINK = "scheme_schemethirdpartyconsentlink.tsv"
    SCHEME_IMAGE = "scheme_schemeimage.tsv"
    SCHEME_WHITELIST = "scheme_schemebundleassociation.tsv"
    # voucher schemes! alternate schemes to be PLR
    # membership plan documents
    # Payment scheme
    # Payment images
    # Provider status mapping
    USER = "users.tsv"
    CONSENT = ("ubiquity_serviceconsent.tsv",)
    SCHEME_ACCOUNT = ("scheme_schemeaccount.tsv",)
    ANSWER = ("scheme_schemeaccountcredentialanswer.tsv",)
    PAYMENT_ACCOUNT = ("payment_card_paymentcardaccount.tsv",)
    PAYMENT_ACCOUNT_ENTRY = ("ubiquity_paymentcardaccountentry.tsv",)
    SCHEME_ACCOUNT_ENTRY = ("ubiquity_schemeaccountentry.tsv",)
    PAYMENT_SCHEME_ENTRY = ("ubiquity_paymentcardschemeentry.tsv",)


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

    organisations = [create_channel.organisation(client) for client in ALL_CLIENTS]
    write_to_tsv(Files.ORGANISATION, organisations)
    client_applications = [create_channel.client_application(client) for client in ALL_CLIENTS]
    write_to_tsv(Files.CLIENT_APP, client_applications)
    client_application_bundle = [create_channel.client_application_bundle(client) for client in ALL_CLIENTS]
    write_to_tsv(Files.CLIENT_APP_BUNDLE, client_application_bundle)

    categories = [create_plan.category()]
    write_to_tsv(Files.CATEGORY, categories)

    membership_plans = []
    plan_questions = []
    scheme_images = []
    scheme_consents = []
    third_party_consents = []
    for count in range(0, MEMBERSHIP_PLANS):
        static_id = STATIC_START_ID + count
        plan_name = f"performance plan {static_id}"
        plan_slug = f"performance-plan-{static_id}"
        membership_plans.append(create_plan.membership_plan(static_id, plan_name, plan_slug))
        plan_questions.append(create_plan.card_no_question(static_id, static_id))
        postcode_question_id = STATIC_START_ID + MEMBERSHIP_PLANS + count
        plan_questions.append(create_plan.postcode_question(postcode_question_id, static_id))
        scheme_images.append(create_plan.scheme_image(static_id, static_id))

        scheme_consent = create_plan.scheme_consent(static_id, static_id)
        scheme_consents.append(scheme_consent)
        plan_third_party_consent_links = create_plan.create_all_third_party_consent_links(static_id)
        third_party_consents.extend(plan_third_party_consent_links)

    write_to_tsv(Files.SCHEME, membership_plans)
    write_to_tsv(Files.QUESTION, plan_questions)
    write_to_tsv(Files.SCHEME_IMAGE, scheme_images)
    write_to_tsv(Files.SCHEME_CONSENT, scheme_consents)
    write_to_tsv(Files.THIRD_PARTY_CONSENT_LINK, third_party_consents)

    whitelist_id = STATIC_START_ID
    whitelist_list = []
    for client_fixture in NON_RESTRICTED_CLIENTS:
        for plan in membership_plans:
            whitelist_id += 1
            plan_id = plan[0]
            whitelist_list.append(create_channel.channel_scheme_whitelist(whitelist_id, client_fixture, plan_id))

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
    #         user_id = LOAD_START_ID + remaining_services
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
    #
    #
    end = time.perf_counter()
    print(f"Elapsed time: {end - start}")


if __name__ == "__main__":
    create_tsv()
