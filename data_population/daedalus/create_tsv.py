import csv
import os
import time
from enum import Enum

import requests

from data_population.daedalus import create_data
from data_population.fixtures import CLIENT_ONE, CLIENT_TWO, CLIENT_RESTRICTED, STATIC_START_ID, MEMBERSHIP_PLAN_IDS
from request_data.membership_plan import ClientBundleIDs
from settings import VAULT_URL, VAULT_TOKEN, CHANNEL_VAULT_PATH

TSV_PATH = f"{os.path.dirname(__file__)}/tsv"
LOAD_START_ID = 2000000
BULK_SIZE = 1000


class Files(str, Enum):
    CHANNEL = "channel.tsv"
    MEMBERSHIP_PLAN = "membership_plan.tsv"
    CHANNEL_WHITELIST = "channel_membership_plan_whitelist.tsv"


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

    client_fixtures = [CLIENT_ONE, CLIENT_TWO, CLIENT_RESTRICTED]
    channels = [create_data.channel(client) for client in client_fixtures]
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

    all_channels = {}
    for client_fixture in client_fixtures:
        all_channels[client_fixture["bundle_id"]] = {
            "jwt_secret": client_fixture["secret"]
        }

    headers = {"X-Vault-Token": VAULT_TOKEN}
    vault_channels = requests.get(f"{VAULT_URL}/v1/secret{CHANNEL_VAULT_PATH}", headers=headers).json()['data']

    if not all(item in vault_channels.items() for item in all_channels.items()):
        all_channels.update(vault_channels)
        requests.post(f"{VAULT_URL}/v1/secret{CHANNEL_VAULT_PATH}", headers=headers, json=all_channels)

    test_keys_url = f"{VAULT_URL}/v1/secret/data/{ClientBundleIDs.BARCLAYS}"
    test_payment_card_keys = requests.get(test_keys_url, headers=headers).json()['data']

    for client in client_fixtures:
        keys_url = f"{VAULT_URL}/v1/secret/data/{client['bundle_id']}"
        resp = requests.get(keys_url, headers=headers)
        if resp.status_code == 404:
            data = test_payment_card_keys
            requests.post(keys_url, headers=headers, json=data)

    end = time.perf_counter()
    print(f"Elapsed time: {end - start}")


if __name__ == "__main__":
    create_tsv()
