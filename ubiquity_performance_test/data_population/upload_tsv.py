import glob
import os
import time
from typing import TYPE_CHECKING

import psycopg2
from loguru import logger

from ubiquity_performance_test.config import settings
from ubiquity_performance_test.data_population.database_tables import HermesTables

if TYPE_CHECKING:
    from enum import StrEnum

    from psycopg2 import connection as connection_class
    from psycopg2 import cursor as cursor_class

    ConnectionType = type[connection_class]
    CursorType = type[cursor_class]


NO_SEQ_TABLES = [HermesTables.CLIENT_APP, HermesTables.CONSENT]


def truncate_table(cur: "CursorType", table_name: str) -> None:
    truncate_statement = f'TRUNCATE "{table_name}" CASCADE'
    cur.execute(truncate_statement)


def delete_client_app_perf_records(cur: "CursorType") -> None:
    organisation_delete = f"DELETE FROM {HermesTables.ORGANISATION} WHERE id <> 1"
    cur.execute(organisation_delete)
    delete_statement = f"DELETE FROM {HermesTables.CLIENT_APP} WHERE organisation_id <> 1"
    cur.execute(delete_statement)


def upload_tsv(cur: "CursorType", table_name: str, tsv: str) -> None:
    with open(tsv) as f:
        cur.copy_from(f, table_name, sep="\t", null="NULL")


def update_seq(cur: "CursorType", table_name: str) -> None:
    if table_name in NO_SEQ_TABLES:
        return

    setval_statement = f"SELECT setval('{table_name}_id_seq', max(id)) FROM \"{table_name}\""
    cur.execute(setval_statement)


def truncate_and_populate_tables(db_name: str, tables: "StrEnum") -> None:
    db_connection_info = psycopg2.extensions.parse_dsn(settings.DB_CONNECTION_URI)
    db_connection_info["dbname"] = db_name

    connection: "ConnectionType"
    cursor: "CursorType"
    with psycopg2.connect(**db_connection_info) as connection, connection.cursor() as cursor:
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
            path = os.path.join(settings.TSV_BASE_DIR, table + "-*.tsv")
            for tsv in glob.glob(path):
                logger.debug(f"Uploading file {tsv} to table {table}")
                upload_tsv(cursor, table, tsv)
            update_seq(cursor, table)


def upload_named_group_of_tsv_files(db_name: str, tables: "StrEnum") -> None:
    start = time.perf_counter()
    truncate_and_populate_tables(db_name, tables)
    logger.debug(f"Completed upload for {tables!s}. Elapsed time: {time.perf_counter() - start}")
