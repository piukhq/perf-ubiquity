import multiprocessing
import os
from enum import Enum


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


class CardTypes(str, Enum):
    MCARD = "mcard"
    PCARD = "pcard"


cores = multiprocessing.cpu_count()


def create_tsv_jobs():
    jobs = init_jobs()
    jobs = add_card_info_to_jobs(jobs, CardTypes.PCARD, TOTAL_PCARDS, PCARDS_PER_SERVICE)
    jobs = add_card_info_to_jobs(jobs, CardTypes.MCARD, TOTAL_MCARDS, MCARDS_PER_SERVICE)
    return jobs


# maybe add both ard type keys when init
def init_jobs():
    jobs = []
    job_id = 0
    service_index = 1
    services_per_job, services_remainder = divmod(TOTAL_USERS, cores)
    for job in range(0, cores):
        jobs.append({
            "job_id": job_id,
            "start": service_index,
            "count": services_per_job,
        })
        service_index += services_per_job
        job_id += 1

    jobs.append({
        "job_id": job_id,
        "start": service_index,
        "count": services_remainder,
    })

    return jobs


def add_card_info_to_jobs(jobs, card_type, total_cards, card_per_service):
    card_index = 1
    remaining_cards = total_cards
    remaining_service_cards = TOTAL_USERS * card_per_service
    if remaining_service_cards >= total_cards:
        remaining_service_cards = total_cards

    # add cards related to services
    for job in jobs:
        card_start = card_index
        card_count = job['count'] * card_per_service

        # refactor card job to only add count when adding things related to services - then remove me
        if card_start >= total_cards:
            card_count = 0
        elif card_start + card_count > total_cards:
            card_count = card_start - total_cards

        if card_count > remaining_service_cards:
            card_count = remaining_service_cards

        job[f"{card_type}_start"] = card_start
        job[f"{card_type}_service_count"] = card_count
        card_index += card_count
        remaining_service_cards -= card_count
        remaining_cards -= card_count

    # if we need to creat more cards, create overflow cards not related to services
    if remaining_cards:
        overflow_cards_per_job = (remaining_cards // len(jobs)) + 1
        for job in jobs:
            overflow_count = overflow_cards_per_job
            if overflow_cards_per_job > remaining_cards:
                overflow_count = remaining_cards

            job[f"{card_type}_overflow_count"] = overflow_count
            remaining_cards -= overflow_count

    fixed_card_start_index = 1
    for job in jobs:
        job[f"{card_type}_start"] = fixed_card_start_index
        fixed_card_start_index += job[f"{card_type}_service_count"] + job[f"{card_type}_overflow_count"]

    return jobs
