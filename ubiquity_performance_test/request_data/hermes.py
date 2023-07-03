import time

import requests
from loguru import logger
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ubiquity_performance_test.locust_angelia.database.jobs import query_status
from ubiquity_performance_test.settings import HERMES_URL, SERVICE_API_KEY

REQUEST_TIMEOUT = 6


def retry_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.3,
        method_whitelist=False,  # type: ignore [arg-type]
        status_forcelist=[500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def headers() -> dict:
    return {"Content-Type": "application/json", "Authorization": f"token {SERVICE_API_KEY}"}


def wait_for_scheme_account_status(status: int, scheme_account_id: int) -> bool:
    current_retry = 0
    timeout = 30
    retry_wait_time = 1
    match = False

    while current_retry < timeout:
        if status in query_status(scheme_account_id):  # 901 = ENROL_FAILED
            match = True
            break
        else:
            time.sleep(retry_wait_time)
            current_retry += retry_wait_time
    if current_retry >= timeout:
        logger.error(
            f"STATUS TIMEOUT: Loyalty Card {scheme_account_id} still not processed after {timeout} seconds. Sending "
            f"request anyway."
        )

    return match


def post_scheme_account_status(status: int, scheme_account_id: int) -> None:
    session = retry_session()
    data = {"status": status}
    auth_header = headers()
    session.post(f"{HERMES_URL}/schemes/accounts/{scheme_account_id}/status", json=data, headers=auth_header)

    wait_for_scheme_account_status(status, scheme_account_id)
