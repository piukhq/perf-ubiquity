import csv
import os
import time
from enum import Enum

from data_population.daedalus import create_data
from data_population.fixtures import CLIENT_ONE, CLIENT_TWO, CLIENT_RESTRICTED, STATIC_START_ID, MEMBERSHIP_PLAN_IDS

TSV_PATH = f"{os.path.dirname(__file__)}/tsv"
LOAD_START_ID = 2000000
BULK_SIZE = 1000
CLIENT_FIXTURES = [CLIENT_ONE, CLIENT_TWO, CLIENT_RESTRICTED]
SERVICE_COUNT = 180_000_000
MCARDS_PER_SERVICE = 8

MEMBERSHIP_COUNT = SERVICE_COUNT * MCARDS_PER_SERVICE


class Files(str, Enum):
    CHANNEL = "channel.tsv"
    MEMBERSHIP_PLAN = "membership_plan.tsv"
    CHANNEL_WHITELIST = "channel_membership_plan_whitelist.tsv"
    SERVICE = "service.tsv"


def tsv_path(file_name):
    return f"{TSV_PATH}/{file_name}"


def write_to_tsv(file_name, rows):
    path = tsv_path(file_name)
    with open(path, "a") as f:
        tsv_writer = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_NONE, escapechar="", quotechar="")
        tsv_writer.writerows(rows)


def create_tsv():
    start = time.perf_counter()
    os.makedirs(TSV_PATH, exist_ok=True)
    for file in Files:
        try:
            os.remove(tsv_path(file))
        except FileNotFoundError:
            pass

    channels = [create_data.channel(client) for client in CLIENT_FIXTURES]
    write_to_tsv(Files.CHANNEL, channels)

    membership_plans = []
    for plan_id in MEMBERSHIP_PLAN_IDS:
        plan_name = f"performance plan {plan_id}"
        membership_plans.append(create_data.membership_plan(plan_id, plan_name))

    write_to_tsv(Files.MEMBERSHIP_PLAN, membership_plans)

    whitelist_id = STATIC_START_ID
    whitelist_list = []
    for client_fixture in [CLIENT_ONE, CLIENT_TWO]:
        for plan in membership_plans:
            whitelist_id += 1
            plan_id = plan[0]
            whitelist_list.append(create_data.channel_whitelist(whitelist_id, client_fixture, plan_id))

    write_to_tsv(Files.CHANNEL_WHITELIST, whitelist_list)

    client_fixtures = [CLIENT_ONE, CLIENT_TWO]
    fixture_count = len(client_fixtures)
    total_services_remaining = SERVICE_COUNT
    print("creating services")

    while total_services_remaining > 0:
        services = []
        batch_counter = BULK_SIZE
        while batch_counter > 0 and total_services_remaining > 0:
            service_id = SERVICE_COUNT - total_services_remaining
            client_fixture = client_fixtures[service_id % fixture_count]
            services.append(
                create_data.service(
                    client_fixture,
                    service_id=service_id,
                    email=f"performanc{service_id}@test.locust"
                )
            )
            batch_counter -= 1
            total_services_remaining -= 1

        write_to_tsv(Files.SERVICE, services)

    # Create Membership Cards

    total_mcards_remaining = MEMBERSHIP_COUNT
    while total_mcards_remaining > 0:
        mcards = []
        batch_counter = BULK_SIZE
        while batch_counter > 0 and total_mcards_remaining > 0:
            mcard_id = MEMBERSHIP_COUNT - total_mcards_remaining
            mcards.append(
                create_data.membership_card(
                    mcard_id=mcard_id,
                    membership_plan_id=client_fixtures[mcard_id % fixture_count]['id'],
                    card_number=f'63317491{mcard_id:010}'
                )
            )

    end = time.perf_counter()
    print(f"Elapsed time: {end - start}")


if __name__ == "__main__":
    create_tsv()
