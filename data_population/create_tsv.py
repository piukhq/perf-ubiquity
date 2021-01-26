import csv
import glob
import logging
import multiprocessing
import os
import random
import time
from enum import Enum

from data_population.create_data import (create_association, create_mcard, create_pcard, create_channel, create_plan,
                                         create_service)
from data_population.fixtures.client import ALL_CLIENTS, NON_RESTRICTED_CLIENTS
from data_population.fixtures.payment_scheme import ALL_PAYMENT_PROVIDER_STATUS_MAPPINGS
from data_population.job_creation import (create_tsv_jobs, cores, MEMBERSHIP_PLANS, CardTypes, MCARDS_PER_SERVICE,
                                          PCARDS_PER_SERVICE, TOTAL_MCARDS, TOTAL_TRANSACTIONS)
from settings import TSV_BASE_DIR

logger = logging.getLogger("create-tsv")

BULK_SIZE = 10000
TRANSACTIONS_PER_MCARD = TOTAL_TRANSACTIONS // TOTAL_MCARDS


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
    PAYMENT_CARD_ACCOUNT_IMAGE = "payment_card_paymentcardaccountimage"
    PROVIDER_STATUS_MAPPING = "payment_card_providerstatusmapping"
    SCHEME_ACCOUNT = "scheme_schemeaccount"
    ANSWER = "scheme_schemeaccountcredentialanswer"
    PAYMENT_ACCOUNT = "payment_card_paymentcardaccount"
    PAYMENT_ACCOUNT_ENTRY = "ubiquity_paymentcardaccountentry"
    SCHEME_ACCOUNT_ENTRY = "ubiquity_schemeaccountentry"
    PAYMENT_MEMBERSHIP_ENTRY = "ubiquity_paymentcardschemeentry"
    VOP_ACTIVATION = "ubiquity_vopactivation"


class HistoryTables(str, Enum):
    HISTORICAL_SCHEME_ACCOUNT = "history_historicalschemeaccount"
    HISTORICAL_PAYMENT_CARD_ACCOUNT = "history_historicalpaymentcardaccount"
    HISTORICAL_PAYMENT_ACCOUNT_ENTRY = "history_historicalpaymentcardaccountentry"
    HISTORICAL_SCHEME_ACCOUNT_ENTRY = "history_historicalschemeaccountentry"
    # not implemented yet
    # HISTORICAL_PAYMENT_MEMBERSHIP_ENTRY = "history_historicalpaymentcardschemeentry"


class HadesTables(str, Enum):
    TRANSACTIONS = "transaction"


class Counters:
    def __init__(self, job):
        self.part = job["job_id"]
        self.users = []
        self.services = []
        self.membership_cards = []
        self.historical_membership_cards = []
        self.membership_card_associations = []
        self.historical_m_card_associations = []
        self.payment_cards = []
        self.historical_payment_cards = []
        self.payment_card_associations = []
        self.historical_p_card_associations = []
        self.pll_links = []
        self.historical_pll_links = []
        self.vop_activation_dict = {}
        self.service_start = job["start"]
        self.mcard_index = job[f"{CardTypes.MCARD}_start"]
        self.mcard_history_index = job[f"historical_{CardTypes.MCARD}_start"]
        self.pcard_index = job[f"{CardTypes.PCARD}_start"]
        self.pcard_history_index = job[f"historical_{CardTypes.PCARD}_start"]
        self.remaining_service_mcards = job[f"{CardTypes.MCARD}_service_count"]
        self.remaining_service_pcards = job[f"{CardTypes.PCARD}_service_count"]
        self.remaining_overflow_mcards = job[f"{CardTypes.MCARD}_overflow_count"]
        self.remaining_overflow_pcards = job[f"{CardTypes.PCARD}_overflow_count"]

    def clear_entries(self):
        for entries in (
                self.users,
                self.services,
                self.membership_cards,
                self.historical_membership_cards,
                self.historical_payment_cards,
                self.membership_card_associations,
                self.historical_m_card_associations,
                self.payment_cards,
                self.payment_card_associations,
                self.historical_p_card_associations,
                self.pll_links,
                self.historical_pll_links,
                self.vop_activation_dict,
        ):
            entries.clear()

    def write_part_to_csv(self):
        write_to_tsv_part(HermesTables.USER, self.part, self.users)
        write_to_tsv_part(HermesTables.CONSENT, self.part, self.services)
        write_to_tsv_part(HermesTables.SCHEME_ACCOUNT, self.part, self.membership_cards)
        write_to_tsv_part(HermesTables.HISTORICAL_SCHEME_ACCOUNT, self.part, self.historical_membership_cards)
        write_to_tsv_part(HermesTables.SCHEME_ACCOUNT_ENTRY, self.part, self.membership_card_associations)
        write_to_tsv_part(HermesTables.HISTORICAL_SCHEME_ACCOUNT_ENTRY, self.part, self.historical_m_card_associations)
        write_to_tsv_part(HermesTables.PAYMENT_ACCOUNT, self.part, self.payment_cards)
        write_to_tsv_part(HermesTables.HISTORICAL_PAYMENT_CARD_ACCOUNT, self.part, self.historical_payment_cards)
        write_to_tsv_part(HermesTables.PAYMENT_ACCOUNT_ENTRY, self.part, self.payment_card_associations)
        write_to_tsv_part(HermesTables.HISTORICAL_PAYMENT_ACCOUNT_ENTRY, self.part, self.historical_p_card_associations)
        write_to_tsv_part(HermesTables.PAYMENT_MEMBERSHIP_ENTRY, self.part, self.pll_links)
        # write_to_tsv_part(HermesTables.HISTORICAL_PAYMENT_MEMBERSHIP_ENTRY, self.part, self.historical_pll_links)
        vop_activation_list = list(self.vop_activation_dict.values())
        write_to_tsv_part(HermesTables.VOP_ACTIVATION, self.part, vop_activation_list)

    def populate_card_history(self, card, card_type):
        if card_type == CardTypes.MCARD:
            for _ in range(random.randint(8, 15)):
                self.historical_membership_cards.append(
                    create_mcard.historical_membership_card(card, self.mcard_history_index))
                self.mcard_history_index += 1

        elif card_type == CardTypes.PCARD:
            for _ in range(random.randint(4, 8)):
                self.historical_payment_cards.append(
                    create_pcard.historical_payment_card(card, self.pcard_history_index))
                self.pcard_history_index += 1


def tsv_path(table_name):
    return f"{TSV_BASE_DIR}/{table_name}.tsv"


def write_to_tsv_part(file_name, part, rows):
    write_to_tsv(file_name + "-" + str(part), rows)


def write_to_tsv(file_name, rows):
    path = tsv_path(file_name)
    with open(path, "a") as f:
        tsv_writer = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_NONE, escapechar="", quotechar="")
        tsv_writer.writerows(rows)


def delete_old_tsv_files(table_enum):
    os.makedirs(TSV_BASE_DIR, exist_ok=True)
    for table in table_enum:
        try:
            path = os.path.join(TSV_BASE_DIR, table + "*.tsv")
            for file in glob.glob(path):
                os.remove(file)
        except FileNotFoundError:
            pass


def create_channel_tsv_files():
    organisations = [create_channel.organisation(client) for client in ALL_CLIENTS]
    write_to_tsv_part(HermesTables.ORGANISATION, 0, organisations)
    client_applications = [create_channel.client_application(client) for client in ALL_CLIENTS]
    write_to_tsv_part(HermesTables.CLIENT_APP, 0, client_applications)
    client_application_bundle = [create_channel.client_application_bundle(client) for client in ALL_CLIENTS]
    write_to_tsv_part(HermesTables.CLIENT_APP_BUNDLE, 0, client_application_bundle)


def create_payment_scheme_tsv_files():
    issuer_names = ["Barclays", "Performance"]
    issuers = [create_pcard.issuer(pk, name) for pk, name in enumerate(issuer_names, 1)]
    write_to_tsv_part(HermesTables.PAYMENT_CARD_ISSUER, 0, issuers)
    payment_schemes = create_pcard.create_all_payment_schemes()
    write_to_tsv_part(HermesTables.PAYMENT_SCHEME, 0, payment_schemes)
    payment_images = create_pcard.create_all_payment_card_images()
    write_to_tsv_part(HermesTables.PAYMENT_CARD_IMAGE, 0, payment_images)
    payment_card_account_images = create_pcard.create_all_payment_card_account_images()
    write_to_tsv_part(HermesTables.PAYMENT_CARD_ACCOUNT_IMAGE, 0, payment_card_account_images)
    write_to_tsv_part(HermesTables.PROVIDER_STATUS_MAPPING, 0, ALL_PAYMENT_PROVIDER_STATUS_MAPPINGS)


def create_membership_plan_tsv_files():
    categories = [create_plan.category()]
    write_to_tsv_part(HermesTables.CATEGORY, 0, categories)

    membership_plans = []
    plan_questions = []
    scheme_images = []
    scheme_balance_details = []
    scheme_contents = []
    membership_plan_documents = []
    scheme_consents = []
    third_party_consents = []
    voucher_schemes = []
    third_party_consent_index = 1
    for count in range(1, MEMBERSHIP_PLANS + 1):
        if count == 1:
            plan_name = f"performance voucher mock {count}"
            plan_slug = f"performance-voucher-mock-{count}"
            voucher_schemes.append(create_plan.voucher_scheme(count, count))
        else:
            plan_name = f"performance mock {count}"
            plan_slug = f"performance-mock-{count}"
        membership_plans.append(create_plan.membership_plan(count, plan_name, plan_slug))
        plan_questions.append(create_plan.card_no_question(count, count))
        password_question_id = MEMBERSHIP_PLANS + count
        plan_questions.append(create_plan.password_question(password_question_id, count))
        scheme_images.append(create_plan.scheme_image(count, count))
        scheme_balance_details.append(create_plan.scheme_balance_details(count, count))
        scheme_contents.append(create_plan.scheme_content(count, count))
        membership_plan_documents.append(create_plan.membership_plan_documents(count, count))
        scheme_consent = create_plan.scheme_consent(count, count)
        scheme_consents.append(scheme_consent)
        total_channels = len(ALL_CLIENTS)
        plan_third_party_consent_links = create_plan.create_all_third_party_consent_links(
            third_party_consent_index, count
        )
        third_party_consent_index += total_channels
        third_party_consents.extend(plan_third_party_consent_links)

    write_to_tsv_part(HermesTables.SCHEME, 0, membership_plans)
    write_to_tsv_part(HermesTables.QUESTION, 0, plan_questions)
    write_to_tsv_part(HermesTables.SCHEME_IMAGE, 0, scheme_images)
    write_to_tsv_part(HermesTables.SCHEME_BALANCE_DETAILS, 0, scheme_balance_details)
    write_to_tsv_part(HermesTables.SCHEME_CONTENT, 0, scheme_contents)
    write_to_tsv_part(HermesTables.MEMBERSHIP_PLAN_DOCUMENTS, 0, membership_plan_documents)
    write_to_tsv_part(HermesTables.SCHEME_CONSENT, 0, scheme_consents)
    write_to_tsv_part(HermesTables.THIRD_PARTY_CONSENT_LINK, 0, third_party_consents)
    write_to_tsv_part(HermesTables.VOUCHER_SCHEME, 0, voucher_schemes)

    whitelist_list = []
    whitelist_id = 0
    for client_fixture in NON_RESTRICTED_CLIENTS:
        for plan in membership_plans:
            whitelist_id += 1
            plan_id = plan[0]
            whitelist_list.append(create_channel.channel_scheme_whitelist(whitelist_id, client_fixture, plan_id))

    write_to_tsv_part(HermesTables.SCHEME_WHITELIST, 0, whitelist_list)


def create_service_mcard_and_pcard_tsv_files():
    jobs = create_tsv_jobs()
    logger.info("Starting jobs")
    pool = multiprocessing.Pool(processes=cores)
    pool.map(create_service_mcard_and_pcard_job, jobs)
    logger.info("Waiting for jobs")
    pool.close()
    pool.join()


def create_service_mcard_and_pcard_job(job):
    counters = Counters(job)
    for service_count in range(0, job["count"]):
        service_pk = counters.service_start + service_count
        if len(counters.users) > BULK_SIZE:
            counters.write_part_to_csv()
            counters.clear_entries()

        counters.users.append(create_service.user(service_pk))
        counters.services.append(create_service.service(service_pk))

        create_pll_link = True
        for mcard_count in range(0, MCARDS_PER_SERVICE):
            if not counters.remaining_service_mcards:
                create_pll_link = False
                break

            scheme_id = random.randint(1, MEMBERSHIP_PLANS)

            mcard = create_mcard.membership_card(counters.mcard_index, scheme_id, TRANSACTIONS_PER_MCARD)
            counters.membership_cards.append(mcard)
            link = create_association.scheme_account(counters.mcard_index, counters.mcard_index, service_pk)
            counters.membership_card_associations.append(link)
            counters.historical_m_card_associations.append(
                create_association.historical_scheme_account(link, counters.mcard_index))

            counters.populate_card_history(mcard, CardTypes.MCARD)
            counters.mcard_index += 1
            counters.remaining_service_mcards -= 1

        for pcard_count in range(0, PCARDS_PER_SERVICE):
            if not counters.remaining_service_pcards:
                create_pll_link = False
                break

            pcard = create_pcard.payment_card(counters.pcard_index)
            counters.payment_cards.append(pcard)
            link = create_association.payment_card(counters.pcard_index, counters.pcard_index, service_pk)
            counters.payment_card_associations.append(link)
            counters.historical_p_card_associations.append(
                create_association.historical_payment_card(link, counters.pcard_index))

            counters.populate_card_history(pcard, CardTypes.PCARD)
            counters.pcard_index += 1
            counters.remaining_service_pcards -= 1

        if create_pll_link:
            link = create_association.pll_link(counters.pcard_index - 1, counters.pcard_index - 1,
                                               counters.mcard_index - 1)
            counters.pll_links.append(link)
            # counters.historical_pll_links.append(create_association.historical_pll_link(
            # link, counters.pcard_index - 1))
            scheme_id = random.randint(1, MEMBERSHIP_PLANS)
            vop_activation = create_association.vop_activation(counters.pcard_index - 1, counters.pcard_index - 1,
                                                               scheme_id)
            counters.vop_activation_dict[counters.pcard_index - 1] = vop_activation

        if service_pk % 100000 == 0:
            logger.info(f"Generated {service_pk} users")

    overflow_mcard_start = job[f"{CardTypes.MCARD}_start"] + len(counters.membership_cards)
    overflow_pcard_start = job[f"{CardTypes.PCARD}_start"] + len(counters.payment_cards)
    (
        overflow_mcards,
        overflow_historical_mcard,
        overflow_pcards,
        overflow_historical_pcards
    ) = create_remaining_mcards_and_pcards(
        overflow_mcard_start,
        counters.mcard_history_index,
        overflow_pcard_start,
        counters.pcard_history_index,
        counters.remaining_overflow_mcards,
        counters.remaining_overflow_pcards
    )

    counters.membership_cards.extend(overflow_mcards)
    counters.historical_membership_cards.extend(overflow_historical_mcard)
    counters.payment_cards.extend(overflow_pcards)
    counters.historical_payment_cards.extend(overflow_historical_pcards)

    counters.write_part_to_csv()

    logger.info(f"Finished {counters.part}")


def create_remaining_mcards_and_pcards(
        mcard_start, mcard_history_index, pcard_start, pcard_history_index, mcard_count, pcard_count
):
    logger.debug(f"Creating overflow cards - mcards: {mcard_count}, pcards: {pcard_count}")
    membership_cards = []
    overflow_historical_mcard = []
    for x in range(0, mcard_count):
        mcard_pk = x + mcard_start
        scheme_id = random.randint(1, MEMBERSHIP_PLANS)
        mcard = create_mcard.membership_card(mcard_pk, scheme_id, TRANSACTIONS_PER_MCARD)
        membership_cards.append(mcard)

        for _ in range(random.randint(8, 15)):
            overflow_historical_mcard.append(create_mcard.historical_membership_card(mcard, mcard_history_index))
            mcard_history_index += 1

    payment_cards = []
    overflow_historical_pcard = []
    for x in range(0, pcard_count):
        pcard_pk = x + pcard_start
        pcard = create_pcard.payment_card(pcard_pk)
        payment_cards.append(pcard)

        for _ in range(random.randint(4, 8)):
            overflow_historical_pcard.append(create_pcard.historical_payment_card(pcard, pcard_history_index))
            pcard_history_index += 1

    return membership_cards, overflow_historical_mcard, payment_cards, overflow_historical_pcard


def create_membership_card_answers():
    cores = multiprocessing.cpu_count()
    answers_per_core = TOTAL_MCARDS // cores
    jobs = []

    for job_id, start in enumerate(range(1, TOTAL_MCARDS + 1, answers_per_core)):
        end = min(start + answers_per_core, TOTAL_MCARDS + 1)

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
        auth_question_pk = add_question_pk + MEMBERSHIP_PLANS
        auth_answers.append(create_mcard.password_answer(auth_answer_pk, add_answer_pk, auth_question_pk))

        if add_answer_pk % 100000 == 0:
            logger.info(f"Generated {add_answer_pk} answers")

    write_to_tsv_part(HermesTables.ANSWER, part, add_answers)
    write_to_tsv_part(HermesTables.ANSWER, part, auth_answers)

    logger.info(f"Finished {part}")


def create_transaction_tsv_files():
    trans_per_core, _ = divmod(TOTAL_TRANSACTIONS, cores)
    jobs = []
    for job_id, start in enumerate(range(1, TOTAL_TRANSACTIONS + 1, trans_per_core)):
        end = min(start + trans_per_core, TOTAL_TRANSACTIONS + 1)

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
