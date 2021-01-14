import glob
import logging
import os
import time

import psycopg2

from data_population.create_tsv import HermesTables, HadesTables, TSV_BASE_DIR
from settings import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, HERMES_DB, HADES_DB

logger = logging.getLogger("upload-tsv")

NO_SEQ_TABLES = [HermesTables.CLIENT_APP, HermesTables.CONSENT]


def postgres_connection(db_name):
    return {
        "user": DB_USER,
        "password": DB_PASSWORD,
        "host": DB_HOST,
        "port": DB_PORT,
        "database": db_name
    }


def truncate_table(cur, table_name):
    formatted_name = format_table_name(table_name)
    truncate_statement = f"TRUNCATE {formatted_name} CASCADE"
    cur.execute(truncate_statement)


def upload_tsv(cur, table_name, tsv):
    with open(tsv) as f:
        formatted_name = format_table_name(table_name)
        cur.copy_from(f, formatted_name, sep="\t", null="NULL")


def update_seq(cur, table_name):
    if table_name in NO_SEQ_TABLES:
        return

    formatted_name = format_table_name(table_name)
    primary_key = format_primary_key(formatted_name)
    setval_statement = (
        f"SELECT setval('{table_name}_{primary_key}_seq', max({primary_key})) FROM {formatted_name}"
    )
    cur.execute(setval_statement)


def format_table_name(table_name):
    if table_name == "user":
        return '"user"'
    return table_name


def format_primary_key(table_name):
    if "historical" in table_name:
        return "history_id"
    return "id"


def truncate_and_populate_tables(db_name, tables):
    connection_info = postgres_connection(db_name)
    with psycopg2.connect(**connection_info) as connection:
        with connection.cursor() as cursor:
            logger.debug(f"Truncating tables defined in `{tables}`")
            for table in tables:
                truncate_table(cursor, table)

            for table in tables:
                path = os.path.join(TSV_BASE_DIR, table + "-*.tsv")
                for tsv in glob.glob(path):
                    logger.debug(f"Uploading file {tsv} to table {table}")
                    upload_tsv(cursor, table, tsv)
                update_seq(cursor, table)


def upload_all_tsv_files():
    start = time.perf_counter()
    truncate_and_populate_tables(HERMES_DB, HermesTables)
    truncate_and_populate_tables(HADES_DB, HadesTables)
    logger.debug(f"Completed upload. Elapsed time: {time.perf_counter() - start}")


def upload_single_tsv_file(db_name, table_name):
    start = time.perf_counter()
    truncate_and_populate_tables(db_name, [table_name])
    logger.debug(f"Completed upload. Elapsed time: {time.perf_counter() - start}")


if __name__ == "__main__":
    upload_all_tsv_files()
