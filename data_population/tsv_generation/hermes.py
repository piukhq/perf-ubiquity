import logging
import multiprocessing
import random
import time
from functools import partial

from data_population.data_population_config import DataConfig
from data_population.database_tables import HermesTables
from data_population.fixtures.client import ALL_CLIENTS, NON_RESTRICTED_CLIENTS, TRUSTED_CHANNEL_CLIENTS
from data_population.fixtures.membership_plan import SCHEME_SLUGS
from data_population.fixtures.payment_scheme import ALL_PAYMENT_PROVIDER_STATUS_MAPPINGS
from data_population.job_creation import MCARDS_PER_SERVICE, PCARDS_PER_SERVICE, CardTypes, cores, create_tsv_jobs
from data_population.row_generation import (
    create_association,
    create_channel,
    create_mcard,
    create_pcard,
    create_plan,
    create_service,
)
from data_population.tsv_generation.common import delete_old_tsv_files, write_to_tsv_part

BULK_SIZE = 10000


logger = logging.getLogger(__name__)


class Counters:
    def __init__(self, job):
        self.part = job["job_id"]
        self.users = []
        self.services = []
        self.membership_cards = []
        self.membership_card_associations = []
        self.membership_card_answers = []
        self.payment_cards = []
        self.payment_card_associations = []
        self.pll_links = []
        self.pll_user_associations = []
        self.vop_activation_dict = {}
        self.service_start = job["start"]
        self.mcard_index = job[f"{CardTypes.MCARD}_start"]
        self.pcard_index = job[f"{CardTypes.PCARD}_start"]
        self.remaining_service_mcards = job[f"{CardTypes.MCARD}_service_count"]
        self.remaining_service_pcards = job[f"{CardTypes.PCARD}_service_count"]
        self.remaining_overflow_mcards = job[f"{CardTypes.MCARD}_overflow_count"]
        self.remaining_overflow_pcards = job[f"{CardTypes.PCARD}_overflow_count"]

    def clear_entries(self):
        for entries in (
            self.users,
            self.services,
            self.membership_cards,
            self.membership_card_associations,
            self.membership_card_answers,
            self.payment_cards,
            self.payment_card_associations,
            self.pll_links,
            self.pll_user_associations,
            self.vop_activation_dict,
        ):
            entries.clear()

    def write_part_to_csv(self):
        write_to_tsv_part(HermesTables.USER, self.part, self.users)
        write_to_tsv_part(HermesTables.CONSENT, self.part, self.services)
        write_to_tsv_part(HermesTables.SCHEME_ACCOUNT, self.part, self.membership_cards)
        write_to_tsv_part(HermesTables.SCHEME_ACCOUNT_ENTRY, self.part, self.membership_card_associations)
        write_to_tsv_part(HermesTables.ANSWER, self.part, self.membership_card_answers)
        write_to_tsv_part(HermesTables.PAYMENT_ACCOUNT, self.part, self.payment_cards)
        write_to_tsv_part(HermesTables.PAYMENT_ACCOUNT_ENTRY, self.part, self.payment_card_associations)
        write_to_tsv_part(HermesTables.PAYMENT_MEMBERSHIP_ENTRY, self.part, self.pll_links)
        write_to_tsv_part(HermesTables.PLL_USER_ASSOCIATION, self.part, self.pll_user_associations)
        vop_activation_list = list(self.vop_activation_dict.values())
        write_to_tsv_part(HermesTables.VOP_ACTIVATION, self.part, vop_activation_list)


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


def create_membership_plan_tsv_files(total_plans: int, real_plans: bool = False):
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
    mcard_range = range(1, len(SCHEME_SLUGS) + 1) if real_plans else range(1, total_plans + 1)
    for count in mcard_range:
        if real_plans:
            plan_name = list(SCHEME_SLUGS.values())[count - 1]
            plan_slug = list(SCHEME_SLUGS.keys())[count - 1]
        else:
            if count % 2 == 0:  # Even-numbered plans are non-voucher
                plan_name = f"performance mock {count}"
                plan_slug = f"performance-mock-{count}"
            else:  # Odd-numbered plans are voucher plans
                plan_name = f"performance voucher mock {count}"
                plan_slug = f"performance-voucher-mock-{count}"
                voucher_schemes.append(create_plan.voucher_scheme(count, count))

        membership_plans.append(create_plan.membership_plan(count, plan_name, plan_slug))
        plan_questions.append(create_plan.card_no_question(count, count))
        password_question_id = total_plans + count
        plan_questions.append(create_plan.password_question(password_question_id, count))
        first_name_question_id = (total_plans * 2) + count
        plan_questions.append(create_plan.first_name_question(first_name_question_id, count))
        merchant_identifier_question_id = (total_plans * 3) + count
        plan_questions.append(create_plan.merchant_identifier_question(merchant_identifier_question_id, count))
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
    for client_fixture in NON_RESTRICTED_CLIENTS + TRUSTED_CHANNEL_CLIENTS:
        for plan in membership_plans:
            whitelist_id += 1
            plan_id = plan[0]
            whitelist_list.append(create_channel.channel_scheme_whitelist(whitelist_id, client_fixture, plan_id))

    write_to_tsv_part(HermesTables.SCHEME_WHITELIST, 0, whitelist_list)


def create_service_mcard_and_pcard_tsv_files(data_config: DataConfig):
    jobs = create_tsv_jobs(
        data_config.payment_cards,
        data_config.payment_cards_history,
        data_config.membership_cards,
        data_config.membership_cards_history,
        data_config.users,
        data_config.users_history,
    )
    logger.info(f"Starting {len(jobs)} jobs for hermes user data...")
    pool = multiprocessing.Pool(processes=cores)
    transactions_per_mcard = data_config.transactions // data_config.membership_cards
    create_data_func = partial(
        create_service_mcard_and_pcard_job,
        data_config.membership_plans,
        data_config.membership_cards,
        transactions_per_mcard,
    )
    pool.map(create_data_func, jobs)
    pool.close()
    pool.join()


def create_service_mcard_and_pcard_job(total_plans: int, total_mcards: int, transactions_per_mcard: int, job: dict):
    counters = Counters(job)
    for service_count in range(0, job["count"]):
        service_pk = counters.service_start + service_count
        if len(counters.users) > BULK_SIZE:
            counters.write_part_to_csv()
            counters.clear_entries()

        new_user = create_service.user(service_pk)
        counters.users.append(new_user)
        counters.services.append(create_service.service(service_pk))

        create_pll_link = True
        for mcard_count in range(0, MCARDS_PER_SERVICE):
            if not counters.remaining_service_mcards:
                create_pll_link = False
                break

            scheme_id = random.randint(1, total_plans)

            mcard = create_mcard.membership_card(counters.mcard_index, scheme_id, transactions_per_mcard)
            counters.membership_cards.append(mcard)
            link = create_association.scheme_account(counters.mcard_index, counters.mcard_index, service_pk)
            counters.membership_card_associations.append(link)

            add_question_pk = scheme_id
            counters.membership_card_answers.append(
                create_mcard.card_number_answer(counters.mcard_index, add_question_pk, counters.mcard_index)
            )

            auth_answer_pk = total_mcards + counters.mcard_index
            auth_question_pk = total_plans + add_question_pk
            counters.membership_card_answers.append(
                create_mcard.password_answer(auth_answer_pk, auth_question_pk, counters.mcard_index)
            )

            merchant_id_answer_pk = (total_mcards * 2) + counters.mcard_index
            merchant_id_question_pk = (total_plans * 2) + add_question_pk
            counters.membership_card_answers.append(
                create_mcard.merchant_identifier_answer(
                    merchant_id_answer_pk, merchant_id_question_pk, counters.mcard_index
                )
            )

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

            counters.pcard_index += 1
            counters.remaining_service_pcards -= 1

        if create_pll_link:
            link = create_association.pll_link(
                counters.pcard_index - 1, counters.pcard_index - 1, counters.mcard_index - 1
            )
            pll_user_association = create_association.pll_user_association(
                counters.pcard_index - 1, counters.pcard_index - 1, service_pk
            )

            counters.pll_links.append(link)
            counters.pll_user_associations.append(pll_user_association)
            scheme_id = random.randint(1, total_plans)
            vop_activation = create_association.vop_activation(
                counters.pcard_index - 1, counters.pcard_index - 1, scheme_id
            )
            counters.vop_activation_dict[counters.pcard_index - 1] = vop_activation

        if service_pk % 100000 == 0:
            logger.info("Generated 100000 users")

    overflow_mcard_start = job[f"{CardTypes.MCARD}_start"] + len(counters.membership_cards)
    overflow_pcard_start = job[f"{CardTypes.PCARD}_start"] + len(counters.payment_cards)
    (overflow_mcards, overflow_pcards,) = create_remaining_mcards_and_pcards(
        overflow_mcard_start,
        overflow_pcard_start,
        counters.remaining_overflow_mcards,
        counters.remaining_overflow_pcards,
        total_plans,
        transactions_per_mcard,
    )

    counters.membership_cards.extend(overflow_mcards)
    counters.payment_cards.extend(overflow_pcards)

    counters.write_part_to_csv()

    logger.info(f"Finished {counters.part}")


def create_remaining_mcards_and_pcards(
    mcard_start: int,
    pcard_start: int,
    mcard_count: int,
    pcard_count: int,
    total_plans: int,
    transactions_per_mcard: int,
):
    logger.debug(f"Creating overflow cards - mcards: {mcard_count}, pcards: {pcard_count}")
    membership_cards = []
    for x in range(0, mcard_count):
        mcard_pk = x + mcard_start
        scheme_id = random.randint(1, total_plans)
        mcard = create_mcard.membership_card(mcard_pk, scheme_id, transactions_per_mcard)
        membership_cards.append(mcard)

    payment_cards = []
    for x in range(0, pcard_count):
        pcard_pk = x + pcard_start
        pcard = create_pcard.payment_card(pcard_pk)
        payment_cards.append(pcard)

    return membership_cards, payment_cards


def create_tsv_files(data_config: DataConfig):
    start = time.perf_counter()

    logger.debug("Deleting old hermes tsv files...")
    delete_old_tsv_files(HermesTables)
    logger.debug(f"Completed deletion. Elapsed time: {time.perf_counter() - start}")

    logger.debug("Creating channel tsv files (1/4)...")
    create_channel_tsv_files()
    logger.debug(f"Completed channels (1/4). Elapsed time: {time.perf_counter() - start}")

    logger.debug("Creating payment scheme tsv files (2/4)...")
    create_payment_scheme_tsv_files()
    logger.debug(f"Completed payment schemes (2/4). Elapsed time: {time.perf_counter() - start}")

    logger.debug("Creating membership plan tsv files (3/4)...")
    create_membership_plan_tsv_files(data_config.membership_plans, data_config.real_plans)
    logger.debug(f"Completed membership plans (3/4). Elapsed time: {time.perf_counter() - start}")

    logger.debug("Creating service, mcard and pcard tsv files (4/4)...")
    create_service_mcard_and_pcard_tsv_files(data_config)
    logger.debug(f"Completed services, mcards and pcards (4/4). Elapsed time: {time.perf_counter() - start}")
