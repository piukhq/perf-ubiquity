import csv
import glob
import os
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING

from ubiquity_performance_test.settings import TSV_BASE_DIR

if TYPE_CHECKING:
    from enum import StrEnum


def tsv_path(table_name: str) -> str:
    return f"{TSV_BASE_DIR}/{table_name}.tsv"


def write_to_tsv_part(file_name: str, part: int, rows: list) -> None:
    write_to_tsv(file_name + "-" + str(part), rows)


def write_to_tsv(file_name: str, rows: list) -> None:
    path = tsv_path(file_name)

    with open(path, "a") as f:
        tsv_writer = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_NONE, escapechar=None, quotechar=None)
        tsv_writer.writerows(rows)


def delete_old_tsv_files(table_enum: type["StrEnum"]) -> None:
    Path(TSV_BASE_DIR).mkdir(exist_ok=True, parents=True)

    for table in table_enum:
        with suppress(FileNotFoundError):
            path = os.path.join(TSV_BASE_DIR, table + "*.tsv")
            for file in glob.glob(path):
                Path(file).unlink()
