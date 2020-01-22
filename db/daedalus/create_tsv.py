import csv
import os
import time
from enum import Enum

from db.daedalus import create_data
from settings import TSV_PATH

TSV_PATH = f"{TSV_PATH}/"
START_ID = 2000000
TOTAL_RECORDS = 10000
BULK_SIZE = 1000


class Files(str, Enum):
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

    print("Creating scheme data...")
    membership_plans = [create_data.membership_plan()]
    write_to_tsv(Files.MEMBERSHIP_PLAN, membership_plans)
    channel_whitelist = [create_data.channel_whitelist()]
    write_to_tsv(Files.CHANNEL_WHITELIST, channel_whitelist)

    end = time.perf_counter()
    print(f"Elapsed time: {end - start}")


if __name__ == "__main__":
    create_tsv()
