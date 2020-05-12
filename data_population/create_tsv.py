import csv
import logging
import os
import random
import time
import multiprocessing
import glob
from enum import Enum

from data_population.fixtures.client import ALL_CLIENTS, NON_RESTRICTED_CLIENTS
from data_population.fixtures.payment_scheme import ALL_PAYMENT_PROVIDER_STATUS_MAPPINGS
from data_population.create_data import (
    create_association,
    create_mcard,
    create_pcard,
    create_channel,
    create_plan,
    create_service,
)
from settings import TSV_PATH

logger = logging.getLogger("create-tsv")

BULK_SIZE = 10000

MEMBERSHIP_PLANS = int(os.environ.get("MEMBERSHIP_PLANS", "6"))
TOTAL_USERS = int(os.environ.get("TOTAL_USERS", "500"))
TOTAL_MCARDS = int(os.environ.get("TOTAL_MCARDS", "5000"))
TOTAL_PCARDS = int(os.environ.get("TOTAL_PCARDS", "2000"))
TOTAL_TRANSACTIONS = int(os.environ.get("TOTAL_TRANSACTIONS", "10000"))

# MEMBERSHIP_PLANS = 40
# TOTAL_USERS = 13017000
# TOTAL_MCARDS = 88953620
# TOTAL_PCARDS = 19525500
# TOTAL_TRANSACTIONS = 889536200

# MEMBERSHIP_PLANS = 100
# TOTAL_USERS = 27494000
# TOTAL_MCARDS = 188265840
# TOTAL_PCARDS = 41241000
# TOTAL_TRANSACTIONS = 1882658400

MCARDS_PER_SERVICE = 7
PCARDS_PER_SERVICE = 2


class HermesTables(str, Enum):
    ORGANISATION = "user_organisation"
    CLIENT_APP = "user_clientapplication"
    CLIENT_APP_BUNDLE = "user_clientapplicationbundle"
    USER = "user"
    CONSENT = "ubiquity_serviceconsent"
    CATEGORY = "scheme_category"
    SCHEME = "scheme_scheme"
    SCHEME_BALANCE_DETAILS = "scheme_schemebalancedetails"
    # SCHEME_FEE = "scheme_schemefee"  # No schemes have fees setup yet
    SCHEME_CONTENT = "scheme_schemecontent"
    QUESTION = "scheme_schemecredentialquestion"
    SCHEME_CONSENT = "scheme_consent"
    THIRD_PARTY_CONSENT_LINK = "scheme_thirdpartyconsentlink"
    SCHEME_IMAGE = "scheme_schemeimage"
    SCHEME_WHITELIST = "scheme_schemebundleassociation"
    VOUCHER_SCHEME = "scheme_voucherscheme"
    MEMBERSHIP_PLAN_DOCUMENTS = "ubiquity_membershipplandocument"
    PAYMENT_CARD_ISSUER = "payment_card_issuer"
    PAYMENT_SCHEME = "payment_card_paymentcard"
    PAYMENT_CARD_IMAGE = "payment_card_paymentcardimage"
    PROVIDER_STATUS_MAPPING = "payment_card_providerstatusmapping"
    SCHEME_ACCOUNT = "scheme_schemeaccount"
    ANSWER = "scheme_schemeaccountcredentialanswer"
    PAYMENT_ACCOUNT = "payment_card_paymentcardaccount"
    PAYMENT_ACCOUNT_ENTRY = "ubiquity_paymentcardaccountentry"
    SCHEME_ACCOUNT_ENTRY = "ubiquity_schemeaccountentry"
    PAYMENT_MEMBERSHIP_ENTRY = "ubiquity_paymentcardschemeentry"


class HadesTables(str, Enum):
    TRANSACTIONS = "transaction"


def tsv_path(table_name):
    return f"{TSV_PATH}/{table_name}.tsv"


def write_to_tsv_part(file_name, part, rows):
    write_to_tsv(file_name + "-" + str(part), rows)


def write_to_tsv(file_name, rows):
    path = tsv_path(file_name)
    with open(path, "a") as f:
        tsv_writer = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_NONE, escapechar="", quotechar="")
        tsv_writer.writerows(rows)


def delete_old_tsv_files(table_enum):
    os.makedirs(TSV_PATH, exist_ok=True)
    for table in table_enum:
        try:
            path = os.path.join(TSV_PATH, table + "*.tsv")
            for file in glob.glob(path):
                os.remove(file)
        except FileNotFoundError:
            pass


def create_channel_tsv_files():
    organisations = [create_channel.organisation(client) for client in ALL_CLIENTS]
    write_to_tsv(HermesTables.ORGANISATION, organisations)
    client_applications = [create_channel.client_application(client) for client in ALL_CLIENTS]
    write_to_tsv(HermesTables.CLIENT_APP, client_applications)
    client_application_bundle = [create_channel.client_application_bundle(client) for client in ALL_CLIENTS]
    write_to_tsv(HermesTables.CLIENT_APP_BUNDLE, client_application_bundle)


def create_payment_scheme_tsv_files():
    issuer_names = ["Barclays", "Performance"]
    issuers = [create_pcard.issuer(pk, name) for pk, name in enumerate(issuer_names, 1)]
    write_to_tsv(HermesTables.PAYMENT_CARD_ISSUER, issuers)
    payment_schemes = create_pcard.create_all_payment_schemes()
    write_to_tsv(HermesTables.PAYMENT_SCHEME, payment_schemes)
    payment_images = create_pcard.create_all_payment_card_images()
    write_to_tsv(HermesTables.PAYMENT_CARD_IMAGE, payment_images)
    write_to_tsv(HermesTables.PROVIDER_STATUS_MAPPING, ALL_PAYMENT_PROVIDER_STATUS_MAPPINGS)


def create_membership_plan_tsv_files():
    categories = [create_plan.category()]
    write_to_tsv(HermesTables.CATEGORY, categories)

    membership_plans = []
    plan_questions = []
    scheme_images = []
    scheme_balance_details = []
    scheme_contents = []
    membership_plan_documents = []
    scheme_consents = []
    third_party_consents = []
    voucher_schemes = []
    for count in range(1, MEMBERSHIP_PLANS + 1):
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
        total_channels = len(ALL_CLIENTS)
        plan_third_party_consent_links = create_plan.create_all_third_party_consent_links(total_channels * count, count)
        third_party_consents.extend(plan_third_party_consent_links)
        if count == 1:
            voucher_schemes.append(create_plan.voucher_scheme(count, count))

    write_to_tsv(HermesTables.SCHEME, membership_plans)
    write_to_tsv(HermesTables.QUESTION, plan_questions)
    write_to_tsv(HermesTables.SCHEME_IMAGE, scheme_images)
    write_to_tsv(HermesTables.SCHEME_BALANCE_DETAILS, scheme_balance_details)
    write_to_tsv(HermesTables.SCHEME_CONTENT, scheme_contents)
    write_to_tsv(HermesTables.MEMBERSHIP_PLAN_DOCUMENTS, membership_plan_documents)
    write_to_tsv(HermesTables.SCHEME_CONSENT, scheme_consents)
    write_to_tsv(HermesTables.THIRD_PARTY_CONSENT_LINK, third_party_consents)
    write_to_tsv(HermesTables.VOUCHER_SCHEME, voucher_schemes)

    whitelist_list = []
    whitelist_id = 0
    for client_fixture in NON_RESTRICTED_CLIENTS:
        for plan in membership_plans:
            whitelist_id += 1
            plan_id = plan[0]
            whitelist_list.append(create_channel.channel_scheme_whitelist(whitelist_id, client_fixture, plan_id))

    write_to_tsv(HermesTables.SCHEME_WHITELIST, whitelist_list)


def create_service_mcard_and_pcard_tsv_files():
    cores = multiprocessing.cpu_count()

    services_per_core, remaining_services11 = divmod(TOTAL_USERS, cores)
    mcards_for_job = services_per_core * (MCARDS_PER_SERVICE + 1)
    pcards_for_job = services_per_core * (PCARDS_PER_SERVICE + 1)

    jobs = []

    mcards_idx = 0
    pcards_idx = 0
    for job_id, service_index in enumerate(range(0, TOTAL_USERS, services_per_core)):
        mstart = min(mcards_idx, TOTAL_MCARDS)
        pstart = min(pcards_idx, TOTAL_PCARDS)

        jobs.append(
            {
                "job_id": job_id,
                "start": service_index,
                "end": service_index + services_per_core,  # used in range, so this is the end+1
                "mcards_start": mstart,
                "mcards_count": min(mcards_idx + mcards_for_job, TOTAL_MCARDS) - mstart,
                "pcards_start": pstart,
                "pcards_count": min(pcards_idx + pcards_for_job, TOTAL_PCARDS) - pstart,
            }
        )

        mcards_idx += mcards_for_job
        pcards_idx += pcards_for_job

    logger.info("Starting jobs")
    pool = multiprocessing.Pool(processes=cores)
    pool.map(create_service_mcard_and_pcard_job, jobs)
    logger.info("Waiting for jobs")
    pool.close()
    pool.join()


def create_service_mcard_and_pcard_job(job):
    part = job["job_id"]
    users = []
    services = []
    membership_cards = []
    membership_card_associations = []
    payment_cards = []
    payment_card_associations = []
    pll_links = []

    mcard_start = job["mcards_start"]
    pcard_start = job["pcards_start"]
    for service_pk in range(job["start"], job["end"]):
        if len(users) > BULK_SIZE:
            write_to_tsv_part(HermesTables.USER, part, users)
            write_to_tsv_part(HermesTables.CONSENT, part, services)
            write_to_tsv_part(HermesTables.SCHEME_ACCOUNT, part, membership_cards)
            write_to_tsv_part(HermesTables.SCHEME_ACCOUNT_ENTRY, part, membership_card_associations)
            write_to_tsv_part(HermesTables.PAYMENT_ACCOUNT, part, payment_cards)
            write_to_tsv_part(HermesTables.PAYMENT_ACCOUNT_ENTRY, part, payment_card_associations)
            write_to_tsv_part(HermesTables.PAYMENT_MEMBERSHIP_ENTRY, part, pll_links)
            for l in (
                users,
                services,
                membership_cards,
                membership_card_associations,
                payment_cards,
                payment_card_associations,
                pll_links,
            ):
                l.clear()

        users.append(create_service.user(service_pk))
        services.append(create_service.service(service_pk))

        mcard_pk = None
        pcard_pk = None
        for mcard_pk in range(min(mcard_start, TOTAL_MCARDS), min(mcard_start + MCARDS_PER_SERVICE, TOTAL_MCARDS)):
            scheme_id = random.randint(1, MEMBERSHIP_PLANS)
            membership_cards.append(create_mcard.membership_card(mcard_pk, scheme_id))
            membership_card_associations.append(create_association.scheme_account(mcard_pk, mcard_pk, service_pk))
        mcard_start += MCARDS_PER_SERVICE

        for pcard_pk in range(min(pcard_start, TOTAL_PCARDS), min(pcard_start + PCARDS_PER_SERVICE, TOTAL_PCARDS)):
            payment_cards.append(create_pcard.payment_card(pcard_pk))
            payment_card_associations.append(create_association.payment_card(pcard_pk, pcard_pk, service_pk))
        pcard_start += PCARDS_PER_SERVICE

        if mcard_pk is not None and pcard_pk is not None:
            pll_links.append(create_association.pll_link(pcard_pk, pcard_pk, mcard_pk))

        if service_pk % 100000 == 0:
            logger.info(f"Generated {service_pk} users")

    write_to_tsv_part(HermesTables.USER, part, users)
    write_to_tsv_part(HermesTables.CONSENT, part, services)
    write_to_tsv_part(HermesTables.SCHEME_ACCOUNT, part, membership_cards)
    write_to_tsv_part(HermesTables.SCHEME_ACCOUNT_ENTRY, part, membership_card_associations)
    write_to_tsv_part(HermesTables.PAYMENT_ACCOUNT, part, payment_cards)
    write_to_tsv_part(HermesTables.PAYMENT_ACCOUNT_ENTRY, part, payment_card_associations)
    write_to_tsv_part(HermesTables.PAYMENT_MEMBERSHIP_ENTRY, part, pll_links)

    logger.info(f"Finished {part}")


def create_remaining_mcards_and_pcards(remaining_mcards, remaining_pcards):
    logger.debug(f"All wallets created. Creating overflow mcards {remaining_mcards} " f"and pcards: {remaining_pcards}")
    while remaining_mcards > 0:
        membership_cards = []
        for _ in range(BULK_SIZE):
            if remaining_mcards <= 0:
                break
            scheme_id = random.randint(1, MEMBERSHIP_PLANS)
            membership_cards.append(create_mcard.membership_card(remaining_mcards, scheme_id))
            remaining_mcards -= 1

        write_to_tsv(HermesTables.SCHEME_ACCOUNT, membership_cards)

    while remaining_pcards > 0:
        payment_cards = []
        for _ in range(BULK_SIZE):
            if remaining_pcards <= 0:
                break
            payment_cards.append(create_pcard.payment_card(remaining_pcards))
            remaining_pcards -= 1


def create_membership_card_answers():
    cores = multiprocessing.cpu_count()
    answers_per_core, _ = divmod(TOTAL_MCARDS, cores)
    jobs = []

    for job_id, start in enumerate(range(0, TOTAL_MCARDS, answers_per_core)):
        end = min(start + answers_per_core, TOTAL_MCARDS)

        jobs.append({"job_id": job_id, "start": start, "count": end - start})

    logger.info("Starting jobs")
    pool = multiprocessing.Pool(processes=cores)
    pool.map(create_membership_card_answers_job, jobs)
    logger.info("Waiting for jobs")
    pool.close()
    pool.join()


def create_membership_card_answers_job(job):
    part = job["job_id"]
    start = job["start"]
    count = job["count"]

    add_answers = []
    auth_answers = []
    for add_answer_pk in range(start, start + count):
        if len(add_answers) > BULK_SIZE:
            write_to_tsv_part(HermesTables.ANSWER, part, add_answers)
            write_to_tsv_part(HermesTables.ANSWER, part, auth_answers)
            add_answers.clear()
            auth_answers.clear()

        add_question_pk = random.randint(1, MEMBERSHIP_PLANS)
        add_answers.append(create_mcard.card_number_answer(add_answer_pk, add_answer_pk, add_question_pk))
        auth_answer_pk = TOTAL_MCARDS + add_answer_pk
        auth_question_pk = add_question_pk + 1
        auth_answers.append(create_mcard.postcode_answer(auth_answer_pk, add_answer_pk, auth_question_pk))

        if add_answer_pk % 100000 == 0:
            logger.info(f"Generated {add_answer_pk} answers")

    write_to_tsv_part(HermesTables.ANSWER, part, add_answers)
    write_to_tsv_part(HermesTables.ANSWER, part, auth_answers)

    logger.info(f"Finished {part}")


def create_transaction_tsv_files():
    cores = multiprocessing.cpu_count()
    trans_per_core, _ = divmod(TOTAL_TRANSACTIONS, cores)
    jobs = []

    for job_id, start in enumerate(range(0, TOTAL_TRANSACTIONS, trans_per_core)):
        end = min(start + trans_per_core, TOTAL_TRANSACTIONS)

        jobs.append({"job_id": job_id, "start": start, "count": end - start})

    logger.info("Starting jobs")
    pool = multiprocessing.Pool(processes=cores)
    pool.map(create_transaction_tsv_job, jobs)
    logger.info("Waiting for jobs")
    pool.close()
    pool.join()


def create_transaction_tsv_job(job):
    part = job["job_id"]
    start = job["start"]
    count = job["count"]

    transactions = []
    for pk in range(start, start + count):
        if len(transactions) > 10000:
            write_to_tsv_part(HadesTables.TRANSACTIONS, part, transactions)
            transactions.clear()

        transactions.append(create_mcard.transaction(pk, pk))

        if pk % 1000000 == 0:
            logger.info(f"Generated {pk} transactions")

    write_to_tsv_part(HadesTables.TRANSACTIONS, part, transactions)
    logger.info(f"Finished {part}")


def create_tsv_files():
    start = time.perf_counter()
    logger.debug("Deleting old tsv files...")
    delete_old_tsv_files(HermesTables)
    delete_old_tsv_files(HadesTables)
    logger.debug(f"Completed deletion. Elapsed time: {time.perf_counter() - start}")
    logger.debug("Creating channel tsv files...")
    create_channel_tsv_files()
    logger.debug(f"Completed channels. Elapsed time: {time.perf_counter() - start}")
    logger.debug("Creating payment scheme tsv files...")
    create_payment_scheme_tsv_files()
    logger.debug(f"Completed payment schemes. Elapsed time: {time.perf_counter() - start}")
    logger.debug("Creating membership plan tsv files...")
    create_membership_plan_tsv_files()
    logger.debug(f"Completed membership plans. Elapsed time: {time.perf_counter() - start}")
    logger.debug("Creating service, mcard and pcard tsv files...")
    create_service_mcard_and_pcard_tsv_files()
    logger.debug(f"Completed services, mcards and pcards. Elapsed time: {time.perf_counter() - start}")
    logger.debug("Creating mcard answer tsv files...")
    create_membership_card_answers()
    logger.debug(f"Completed mcard answers. Elapsed time: {time.perf_counter() - start}")
    logger.debug("Creating hades transaction tsv files...")
    create_transaction_tsv_files()
    logger.debug(f"Completed tsv generation. Elapsed time: {time.perf_counter() - start}")


if __name__ == "__main__":
    create_tsv_files()
