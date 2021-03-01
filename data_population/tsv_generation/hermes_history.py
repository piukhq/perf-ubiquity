import logging
import multiprocessing
import time
from collections.abc import Callable
from functools import partial

from data_population.data_population_config import DataConfig
from data_population.database_tables import HermesHistoryTables
from data_population.row_generation import create_association, create_mcard, create_pcard, create_service
from data_population.job_creation import cores
from data_population.tsv_generation.common import delete_old_tsv_files, write_to_tsv_part


logger = logging.getLogger(__name__)


def create_history_tsv_job(table_name: str, row_generation_func: Callable[int], job: dict):
    job_id = job["job_id"]
    start_pk = job["start"]
    count = job["count"]
    finish_pk = start_pk + count

    history = []
    for pk in range(start_pk, finish_pk):
        # write to tsv every 10000 history rows generated, then clear the previously generated values and continue
        if len(history) > 10000:
            write_to_tsv_part(table_name, job_id, history)
            history.clear()

        history.append(row_generation_func(pk))

        if pk % 500000 == 0:
            logger.info(f"Job ID: {job_id} - Generated 500000 history rows")

    # write remaining history rows to tsv after above loop has finished
    write_to_tsv_part(table_name, job_id, history)
    logger.info(f"Finished job ID: {job_id}")


def create_history_tsv_files(table_name: str, row_generation_func: Callable[dict, list], total: int):
    history_per_core, _ = divmod(total, cores)
    jobs = []

    job_starts = range(1, total + 1, history_per_core)
    for job_id, job_start in enumerate(job_starts):
        job_end = job_start + history_per_core
        if job_end > total + 1:
            job_end = total + 1

        jobs.append({"job_id": job_id, "start": job_start, "count": job_end - job_start})

    logger.info(f"Starting {len(jobs)} history jobs for {table_name}...")
    pool = multiprocessing.Pool(processes=cores)
    job_function = partial(create_history_tsv_job, table_name, row_generation_func)
    pool.map(job_function, jobs)
    pool.close()
    pool.join()


def create_tsv_files(data_config: DataConfig):
    start = time.perf_counter()
    logger.debug("Deleting old hermes history tsv files...")
    delete_old_tsv_files(HermesHistoryTables)
    logger.debug(f"Completed deletion. Elapsed time: {time.perf_counter() - start}")

    logger.debug("Creating historic scheme account tsv files (1/6)...")
    create_history_tsv_files(HermesHistoryTables.HISTORICAL_SCHEME_ACCOUNT,
                             create_mcard.historical_membership_card, data_config.membership_cards)
    logger.debug(f"Completed historic scheme accounts (1/6). Elapsed time: {time.perf_counter() - start}")

    logger.debug("Creating historic scheme account entry tsv files (2/6)...")
    create_history_tsv_files(HermesHistoryTables.HISTORICAL_SCHEME_ACCOUNT_ENTRY,
                             create_association.historical_scheme_account, data_config.membership_cards)
    logger.debug(f"Completed historic scheme account entries (2/6). Elapsed time: {time.perf_counter() - start}")

    logger.debug("Creating historic payment card account tsv files (3/6)...")
    create_history_tsv_files(HermesHistoryTables.HISTORICAL_PAYMENT_CARD_ACCOUNT,
                             create_pcard.historical_payment_card, data_config.payment_cards)
    logger.debug(f"Completed historic payment card accounts (3/6). Elapsed time: {time.perf_counter() - start}")

    logger.debug("Creating historic payment card account entry tsv files (4/6)...")
    create_history_tsv_files(HermesHistoryTables.HISTORICAL_PAYMENT_ACCOUNT_ENTRY,
                             create_association.historical_payment_card, data_config.payment_cards)
    logger.debug(f"Completed historic payment card account entries (4/6). Elapsed time: {time.perf_counter() - start}")

    logger.debug("Creating historic user tsv files (5/6)...")
    create_history_tsv_files(HermesHistoryTables.HISTORICAL_USER, create_service.historic_user, data_config.users)
    logger.debug(f"Completed historic users (5/6). Elapsed time: {time.perf_counter() - start}")

    logger.debug("Creating historic vop activation tsv files (6/6)...")
    create_history_tsv_files(HermesHistoryTables.HISTORICAL_VOP_ACTIVATION,
                             create_association.historical_vop_activation, data_config.payment_cards)
    logger.debug(f"Completed historic vop activations (6/6). Elapsed time: {time.perf_counter() - start}")
