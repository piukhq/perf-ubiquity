import multiprocessing
from enum import Enum


MCARDS_PER_SERVICE = 7
PCARDS_PER_SERVICE = 2


class CardTypes(str, Enum):
    MCARD = "mcard"
    PCARD = "pcard"


cores = multiprocessing.cpu_count()


def create_tsv_jobs(total_pcards: int, total_mcards: int, total_users: int):
    jobs = init_jobs(total_users)
    jobs = add_card_info_to_jobs(jobs, CardTypes.PCARD, total_pcards, PCARDS_PER_SERVICE, total_users)
    jobs = add_card_info_to_jobs(jobs, CardTypes.MCARD, total_mcards, MCARDS_PER_SERVICE, total_users)
    return jobs


def init_jobs(total_users: int):
    jobs = []
    job_id = 0
    service_index = 1
    services_per_job, services_remainder = divmod(total_users, cores)
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


def fix_indexes_for_card_jobs(jobs: list[dict], card_type: str, history_per_card: int):
    fixed_card_start_index = 1
    card_history_index = 1
    for job in jobs:
        job[f"{card_type}_start"] = fixed_card_start_index
        job[f"historical_{card_type}_start"] = card_history_index
        fixed_card_start_index += job[f"{card_type}_service_count"] + job[f"{card_type}_overflow_count"]
        card_history_index += fixed_card_start_index * history_per_card

    return jobs


def process_not_enough_cards_per_service(jobs: list[dict], card_type: str, remaining_cards: int,
                                         cards_per_service: int):
    for job in jobs:
        job[f"{card_type}_start"] = 0
        job[f"{card_type}_service_count"] = 0

    job_count = 0
    while remaining_cards > 0:
        job_index = job_count % len(jobs)
        cards_to_add = cards_per_service
        if cards_to_add > remaining_cards:
            cards_to_add = remaining_cards

        new_job_total = jobs[job_index][f"{card_type}_service_count"] + cards_to_add
        max_cards_for_job = jobs[job_index]["count"] * cards_per_service
        if new_job_total > max_cards_for_job:
            job_count += 1
            continue

        jobs[job_index][f"{card_type}_service_count"] = new_job_total
        remaining_cards -= cards_to_add
        job_count += 1

    return jobs, remaining_cards


def process_enough_cards_per_service(jobs: list[dict], card_type: str, remaining_cards: int, total_cards: int,
                                     remaining_service_cards: int, cards_per_service: int):
    card_index = 1
    for job in jobs:
        card_start = card_index
        card_count = job['count'] * cards_per_service
        if card_start >= total_cards:
            card_count = 0
        elif card_start + card_count > total_cards:
            card_count = total_cards - card_start + 1

        if card_count > remaining_service_cards:
            card_count = remaining_service_cards

        job[f"{card_type}_start"] = card_start
        job[f"{card_type}_service_count"] = card_count
        card_index += card_count
        remaining_service_cards -= card_count
        remaining_cards -= card_count

    return jobs, remaining_cards


def add_card_info_to_jobs(jobs: list[dict], card_type: str, total_cards: int, cards_per_service: int, total_users: int):
    remaining_cards = total_cards
    remaining_service_cards = total_users * cards_per_service
    history_per_card = 15 if card_type == CardTypes.MCARD else 8
    enough_cards_per_service = True
    if remaining_service_cards > total_cards:
        remaining_service_cards = total_cards
        enough_cards_per_service = False

    if not enough_cards_per_service:
        jobs, remaining_cards = process_not_enough_cards_per_service(jobs, card_type, remaining_cards,
                                                                     cards_per_service)

    else:
        jobs, remaining_cards = process_enough_cards_per_service(jobs, card_type, remaining_cards, total_cards,
                                                                 remaining_service_cards, cards_per_service)

    overflow_cards_per_job = 0
    if remaining_cards:
        overflow_cards_per_job = (remaining_cards // len(jobs)) + 1

    for job in jobs:
        overflow_count = overflow_cards_per_job
        if overflow_cards_per_job > remaining_cards:
            overflow_count = remaining_cards

        job[f"{card_type}_overflow_count"] = overflow_count
        remaining_cards -= overflow_count

    jobs = fix_indexes_for_card_jobs(jobs, card_type, history_per_card)
    return jobs
