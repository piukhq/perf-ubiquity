import logging
import multiprocessing
import time

from data_population.data_population_config import DataConfig
from data_population.database_tables import HadesTables
from data_population.row_generation import create_mcard
from data_population.tsv_generation.common import write_to_tsv_part, delete_old_tsv_files

logger = logging.getLogger(__name__)
cores = multiprocessing.cpu_count()


def create_transaction_tsv_job(job: dict):
    job_id = job["job_id"]
    start_pk = job["start"]
    count = job["count"]
    finish_pk = start_pk + count
    total_transactions = count - start_pk

    transactions = []
    for pk in range(start_pk, finish_pk):
        # write to tsv every 10000 transactions generated, then clear the previously generated values and continue
        if len(transactions) > 10000:
            write_to_tsv_part(HadesTables.TRANSACTIONS, job_id, transactions)
            transactions.clear()

        transactions.append(create_mcard.transaction(pk, pk))

        if pk % 500000 == 0:
            logger.info(f"Job ID: {job_id} - Generated {pk} transactions, "
                        f"{pk/total_transactions}% complete...")

    # write remaining transactions to tsv after above loop has finished
    write_to_tsv_part(HadesTables.TRANSACTIONS, job_id, transactions)
    logger.info(f"Finished job ID: {job_id}")


def create_transaction_tsv_files(total_transactions: int):
    transactions_per_core, _ = divmod(total_transactions, cores)
    jobs = []
    for job_id, start in enumerate(range(1, total_transactions + 1, transactions_per_core)):
        end = min(start + transactions_per_core, total_transactions + 1)

        jobs.append({"job_id": job_id, "start": start, "count": end - start})

    logger.info(f"Starting {len(jobs)} jobs for hades transactions...")
    pool = multiprocessing.Pool(processes=cores)
    pool.map(create_transaction_tsv_job, jobs)
    pool.close()
    pool.join()


def create_tsv_files(data_config: DataConfig):
    start = time.perf_counter()

    logger.debug("Deleting old hades tsv files...")
    delete_old_tsv_files(HadesTables)
    logger.debug(f"Completed deletion. Elapsed time: {time.perf_counter() - start}")

    logger.debug("Creating hades transaction tsv files...")
    create_transaction_tsv_files(data_config.transactions)
    logger.debug(f"Completed hades tsv generation. Elapsed time: {time.perf_counter() - start}")
