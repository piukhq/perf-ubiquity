import csv
import os
import time
from enum import Enum

import requests

from data_population.daedalus import create_data
from data_population.fixtures import CLIENT_ONE, CLIENT_TWO, CLIENT_RESTRICTED
from settings import TSV_PATH, VAULT_URL, VAULT_TOKEN

TSV_PATH = f"{TSV_PATH}/"
LOAD_START_ID = 2000000
STATIC_START_ID = 5000
BULK_SIZE = 1000

MEMBERSHIP_PLANS = 40


class Files(str, Enum):
    CHANNEL = "channel.tsv"
    MEMBERSHIP_PLAN = "membership_plan.tsv"
    CHANNEL_WHITELIST = "channel_membership_plan_whitelist.tsv"


def tsv_path(file_name):
    return f"{TSV_PATH}{file_name}"


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

    client_fixtures = [CLIENT_ONE, CLIENT_TWO, CLIENT_RESTRICTED]
    channels = [create_data.channel(client) for client in client_fixtures]
    write_to_tsv(Files.CHANNEL, channels)

    remaining_membership_plans = MEMBERSHIP_PLANS
    membership_plans = []
    while remaining_membership_plans > 0:
        remaining_membership_plans -= 1
        plan_id = STATIC_START_ID + remaining_membership_plans
        plan_name = f"performance plan {remaining_membership_plans}"
        membership_plans.append(create_data.membership_plan(plan_id, plan_name))

    write_to_tsv(Files.MEMBERSHIP_PLAN, membership_plans)

    whitelist_id = STATIC_START_ID
    whitelist_list = []
    for client_fixture in [CLIENT_ONE, CLIENT_TWO]:
        for plan in membership_plans:
            whitelist_id += 1
            plan_id = plan[0]
            whitelist_list.append(create_data.channel_whitelist(whitelist_id, client_fixture, plan_id))

    for client_fixture in client_fixtures:
        headers = {"X-Vault-Token": VAULT_TOKEN}
        data = {
            client_fixture["bundle_id"]: {
                "jwt_secret": client_fixture["secret"]
            }
        }
        requests.post(f"{VAULT_URL}/v1/secret/channel", headers=headers, json=data)

    end = time.perf_counter()
    print(f"Elapsed time: {end - start}")


if __name__ == "__main__":
    create_tsv()
