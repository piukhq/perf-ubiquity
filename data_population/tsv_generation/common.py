import csv
import glob
import os

from settings import TSV_BASE_DIR


def tsv_path(table_name: str):
    return f"{TSV_BASE_DIR}/{table_name}.tsv"


def write_to_tsv_part(file_name: str, part: int, rows: list):
    write_to_tsv(file_name + "-" + str(part), rows)


def write_to_tsv(file_name: str, rows: list):
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
