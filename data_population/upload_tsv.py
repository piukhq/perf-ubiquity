import glob
import logging
import os
import time
from enum import Enum

import psycopg2

from data_population.database_tables import HermesTables
from settings import DB_CONNECTION_URI, TSV_BASE_DIR

logger = logging.getLogger("upload-tsv")

NO_SEQ_TABLES = [HermesTables.CLIENT_APP, HermesTables.CONSENT]


def truncate_table(cur, table_name):
    truncate_statement = f'TRUNCATE "{table_name}" CASCADE'
    cur.execute(truncate_statement)


def delete_client_app_perf_records(cur,):
    organisation_delete = f"DELETE FROM {HermesTables.ORGANISATION} WHERE id <> 1"
    cur.execute(organisation_delete)
    delete_statement = f"DELETE FROM {HermesTables.CLIENT_APP} WHERE organisation_id <> 1"
    cur.execute(delete_statement)


def upload_tsv(cur, table_name, tsv):
    with open(tsv) as f:
        cur.copy_from(f, table_name, sep="\t", null="NULL")


def update_seq(cur, table_name):
    if table_name in NO_SEQ_TABLES:
        return

    setval_statement = f"SELECT setval('{table_name}_id_seq', max(id)) FROM \"{table_name}\""
    cur.execute(setval_statement)


def truncate_and_populate_tables(db_name: str, tables: Enum):
    db_connection_info = psycopg2.extensions.parse_dsn(DB_CONNECTION_URI)
    db_connection_info["dbname"] = db_name

    with psycopg2.connect(**db_connection_info) as connection:
        with connection.cursor() as cursor:
            logger.debug(f"Truncating tables defined in '{tables}'")
            for table in tables:
                # We need to keep certain django data in the organisation and client application tables
                # So use delete rather than truncate. This allows django admin access
                if table is HermesTables.ORGANISATION:
                    continue
                if table is HermesTables.CLIENT_APP:
                    delete_client_app_perf_records(cursor)
                else:
                    truncate_table(cursor, table)

            for table in tables:
                path = os.path.join(TSV_BASE_DIR, table + "-*.tsv")
                for tsv in glob.glob(path):
                    logger.debug(f"Uploading file {tsv} to table {table}")
                    upload_tsv(cursor, table, tsv)
                update_seq(cursor, table)


def upload_named_group_of_tsv_files(db_name: str, tables: Enum):
    start = time.perf_counter()
    truncate_and_populate_tables(db_name, tables)
    logger.debug(f"Completed upload for {str(tables)}. Elapsed time: {time.perf_counter() - start}")
