import csv
import logging

import psycopg2

from settings import DB_CONNECTION_URI, HERMES_DB, TSV_BASE_DIR

logger = logging.getLogger("generate-harmonia-data")


def _get_token_slug_mapping():
    db_connection_info = psycopg2.extensions.parse_dsn(DB_CONNECTION_URI)
    db_connection_info["dbname"] = HERMES_DB

    with psycopg2.connect(**db_connection_info) as connection:
        with connection.cursor() as cursor:
            logger.debug("Fetching token to slug mappings for Harmonia")
            statement = (
                "SELECT"
                " t2.token, t4.slug, t5.slug, t2.pan_start, t2.pan_end FROM ubiquity_paymentcardschemeentry t1 "
                "INNER JOIN payment_card_paymentcardaccount t2 ON t1.payment_card_account_id=t2.id "
                "INNER JOIN scheme_schemeaccount t3 ON t1.scheme_account_id=t3.id "
                "INNER JOIN scheme_scheme t4 ON t3.scheme_id=t4.id "
                "INNER JOIN payment_card_paymentcard t5 on t5.id = t2.payment_card_id"
            )
            cursor.execute(statement)
            return cursor.fetchall()


def write_token_slug_mapping_file():
    data = _get_token_slug_mapping()
    with open(f"{TSV_BASE_DIR}/harmonia_token_to_slug.csv", "w") as out:
        csv_out = csv.writer(out)
        for row in data:
            csv_out.writerow(row)
