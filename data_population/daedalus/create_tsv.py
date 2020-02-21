import csv
import os
import time
from enum import Enum

from data_population.daedalus import create_data
from data_population.fixtures import CLIENT_ONE, CLIENT_TWO, CLIENT_RESTRICTED, STATIC_START_ID, MEMBERSHIP_PLAN_IDS

TSV_PATH = f"{os.path.dirname(__file__)}/tsv"
LOAD_START_ID = 2000000
SERVICE_BATCH_SIZE = 6
CLIENT_FIXTURES = [CLIENT_ONE, CLIENT_TWO, CLIENT_RESTRICTED]
SERVICE_COUNT = 10
PCARDS_PER_SERVICE = 2
MCARDS_PER_SERVICE = 3

SERVICE_START_ID = STATIC_START_ID
PCARD_START_ID = STATIC_START_ID
PCARD_ASSOCIATION_START_ID = STATIC_START_ID

MCARD_START_ID = STATIC_START_ID
MCARD_ASSOCIATION_START_ID = STATIC_START_ID

MEMBERSHIP_COUNT = SERVICE_COUNT * MCARDS_PER_SERVICE


class Files(str, Enum):
    CHANNEL = "channel.tsv"
    MEMBERSHIP_PLAN = "membership_plan.tsv"
    CHANNEL_WHITELIST = "channel_membership_plan_whitelist.tsv"
    SERVICE = "service.tsv"
    PAYMENT_CARD = "payment_card.tsv"
    PCARD_ASSOCIATION = "payment_card_association.tsv"
    MEMBERSHIP_CARD = "membership_card.tsv"
    MCARD_ASSOCIATION = "membership_card_association.tsv"
    PAYMENT_MEMBERSHIP_ASSOCIATION = 'payment_membership_association.tsv'


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
    whitelist_mapping = {}
    for client_fixture in [CLIENT_ONE, CLIENT_TWO]:
        for plan in membership_plans:
            whitelist_id += 1
            plan_id = plan[0]
            whitelist_list.append(create_data.channel_whitelist(whitelist_id, client_fixture, plan_id))
            whitelist_mapping.update({(client_fixture['id'], plan_id): whitelist_id})

    write_to_tsv(Files.CHANNEL_WHITELIST, whitelist_list)

    client_fixtures = [CLIENT_ONE, CLIENT_TWO]
    fixture_count = len(client_fixtures)
    service_id = SERVICE_START_ID

    pcard_id = PCARD_START_ID
    pcard_association_id = PCARD_ASSOCIATION_START_ID
    mcard_id = MCARD_START_ID
    mcard_association_id = MCARD_ASSOCIATION_START_ID

    services = []
    pcards = []
    mcards = []
    pcard_associations = []
    mcard_associations = []
    payment_membership_associations = []
    total = 0
    final_service_id = service_id + SERVICE_COUNT
    while service_id < final_service_id:
        if final_service_id - service_id < SERVICE_BATCH_SIZE:
            batch_size = final_service_id - service_id
        else:
            batch_size = SERVICE_BATCH_SIZE

        for _ in range(batch_size):
            services.append(
                create_data.service(
                    fixture=client_fixtures[service_id % fixture_count],
                    service_id=service_id,
                    email=f"performance{service_id}@test.locust"
                )
            )
            service_id += 1

            for _ in range(PCARDS_PER_SERVICE):
                pcards.append(
                    create_data.payment_card(
                        payment_card_id=pcard_id,
                        fingerprint=f'fingerprint_{pcard_id}',
                        token=f'token_{pcard_id}'
                    )
                )

                pcard_associations.append(
                    create_data.payment_card_association(
                        association_id=pcard_association_id,
                        service_id=service_id,
                        payment_card_id=pcard_id
                    )
                )
                pcard_id += 1
                pcard_association_id += 1

            for _ in range(MCARDS_PER_SERVICE):
                plan_id = mcard_id % len(MEMBERSHIP_PLAN_IDS) + STATIC_START_ID
                mcards.append(
                    create_data.membership_card(
                        mcard_id=mcard_id,
                        membership_plan_id=plan_id,
                        card_number=f'63317491{mcard_id:010}'
                    )
                )

                mcard_associations.append(
                    create_data.membership_card_association(
                        association_id=mcard_association_id,
                        service_id=service_id,
                        membership_card_id=mcard_id,
                        plan_whitelist_id=whitelist_mapping[(client_fixtures[mcard_id % fixture_count]['id'], plan_id)]
                    )
                )
                mcard_id += 1
                mcard_association_id += 1

            payment_membership_associations.append(
                create_data.payment_membership_association(
                    payment_card_id=pcard_id - 1,
                    membership_card_id=mcard_id - 1,
                )
            )

        total += batch_size

    write_to_tsv(Files.SERVICE, services)
    write_to_tsv(Files.PAYMENT_CARD, pcards)
    write_to_tsv(Files.PCARD_ASSOCIATION, pcard_associations)
    write_to_tsv(Files.MEMBERSHIP_CARD, mcards)
    write_to_tsv(Files.MCARD_ASSOCIATION, mcard_associations)
    write_to_tsv(Files.PAYMENT_MEMBERSHIP_ASSOCIATION, payment_membership_associations)
    end = time.perf_counter()
    print(f"Elapsed time: {end - start}")


if __name__ == "__main__":
    create_tsv()
