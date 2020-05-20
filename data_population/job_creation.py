import multiprocessing
import os
from enum import Enum


MEMBERSHIP_PLANS = int(os.environ.get("MEMBERSHIP_PLANS", "6"))
TOTAL_USERS = int(os.environ.get("TOTAL_USERS", "500"))
TOTAL_MCARDS = int(os.environ.get("TOTAL_MCARDS", "5000"))
TOTAL_PCARDS = int(os.environ.get("TOTAL_PCARDS", "2000"))
TOTAL_TRANSACTIONS = int(os.environ.get("TOTAL_TRANSACTIONS", "10000"))

# Benchmark Test (6 channels)
# MEMBERSHIP_PLANS = int(os.environ.get("MEMBERSHIP_PLANS", "6"))
# TOTAL_USERS = int(os.environ.get("TOTAL_USERS", "449333"))
# TOTAL_MCARDS = int(os.environ.get("TOTAL_MCARDS", "3082426"))
# TOTAL_PCARDS = int(os.environ.get("TOTAL_PCARDS", "674000"))
# TOTAL_TRANSACTIONS = int(os.environ.get("TOTAL_TRANSACTIONS", "30824266"))

# Barclays Day One 2021 Cycle One and Two (6 Channels)
# MEMBERSHIP_PLANS = int(os.environ.get("MEMBERSHIP_PLANS", "18"))
# TOTAL_USERS = int(os.environ.get("TOTAL_USERS", "5392000"))
# TOTAL_MCARDS = int(os.environ.get("TOTAL_MCARDS", "36989120"))
# TOTAL_PCARDS = int(os.environ.get("TOTAL_PCARDS", "8088000"))
# TOTAL_TRANSACTIONS = int(os.environ.get("TOTAL_TRANSACTIONS", "369891200"))

# Barclays 2022 (8 channels)
# MEMBERSHIP_PLANS = int(os.environ.get("MEMBERSHIP_PLANS", "26"))
# TOTAL_USERS = int(os.environ.get("TOTAL_USERS", "8192000"))
# TOTAL_MCARDS = int(os.environ.get("TOTAL_MCARDS", "56197120"))
# TOTAL_PCARDS = int(os.environ.get("TOTAL_PCARDS", "12288000"))
# TOTAL_TRANSACTIONS = int(os.environ.get("TOTAL_TRANSACTIONS", "561971200"))

# Barclays 2023 (10 channels)
# MEMBERSHIP_PLANS = int(os.environ.get("MEMBERSHIP_PLANS", "35"))
# TOTAL_USERS = int(os.environ.get("TOTAL_USERS", "11011000"))
# TOTAL_MCARDS = int(os.environ.get("TOTAL_MCARDS", "75535460"))
# TOTAL_PCARDS = int(os.environ.get("TOTAL_PCARDS", "16516500"))
# TOTAL_TRANSACTIONS = int(os.environ.get("TOTAL_TRANSACTIONS", "755354600"))

# Barclays 2024 (12 channels)
# MEMBERSHIP_PLANS = int(os.environ.get("MEMBERSHIP_PLANS", "50"))
# TOTAL_USERS = int(os.environ.get("TOTAL_USERS", "13593000"))
# TOTAL_MCARDS = int(os.environ.get("TOTAL_MCARDS", "93247980"))
# TOTAL_PCARDS = int(os.environ.get("TOTAL_PCARDS", "20389500"))
# TOTAL_TRANSACTIONS = int(os.environ.get("TOTAL_TRANSACTIONS", "932479800"))

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


def fix_indexes_for_card_jobs(jobs, card_type):
    fixed_card_start_index = 1
    for job in jobs:
        job[f"{card_type}_start"] = fixed_card_start_index
        fixed_card_start_index += job[f"{card_type}_service_count"] + job[f"{card_type}_overflow_count"]

    return jobs


def add_card_info_to_jobs(jobs, card_type, total_cards, card_per_service):
    card_index = 1
    remaining_cards = total_cards
    remaining_service_cards = TOTAL_USERS * card_per_service
    enough_cards_per_service = True
    if remaining_service_cards > total_cards:
        remaining_service_cards = total_cards
        enough_cards_per_service = False

    for job in jobs:
        card_start = card_index
        card_count = job['count'] * card_per_service

        if not enough_cards_per_service:
            card_count = job["count"] // remaining_service_cards + 1

        if card_start >= total_cards:
            card_count = 0
        elif card_start + card_count > total_cards:
            card_count = total_cards - card_start

        if card_count > remaining_service_cards:
            card_count = remaining_service_cards

        job[f"{card_type}_start"] = card_start
        job[f"{card_type}_service_count"] = card_count
        card_index += card_count
        remaining_service_cards -= card_count
        remaining_cards -= card_count

    if remaining_cards:
        overflow_cards_per_job = (remaining_cards // len(jobs)) + 1
        for job in jobs:
            overflow_count = overflow_cards_per_job
            if overflow_cards_per_job > remaining_cards:
                overflow_count = remaining_cards

            job[f"{card_type}_overflow_count"] = overflow_count
            remaining_cards -= overflow_count

    jobs = fix_indexes_for_card_jobs(jobs, card_type)
    return jobs
