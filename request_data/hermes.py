import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from settings import SERVICE_API_KEY, HERMES_URL

REQUEST_TIMEOUT = 30


def retry_session():
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.3,
        method_whitelist=False,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def headers():
    return {
        "Content-Type": "application/json",
        "Authorization": f"token {SERVICE_API_KEY}"
    }


def wait_for_scheme_account_status(status, scheme_account_id):
    auth_header = headers()
    params = {"id": scheme_account_id}
    for _ in range(REQUEST_TIMEOUT):
        resp = requests.get(f"{HERMES_URL}/schemes/accounts/query",
                            headers=auth_header, params=params)

        if resp.json()[0]['status'] == status and resp.json()[0]['card_number']:
            break

        time.sleep(1)


def post_scheme_account_status(status, scheme_account_id):
    session = retry_session()
    data = {"status": status}
    auth_header = headers()
    session.post(f"{HERMES_URL}/schemes/accounts/{scheme_account_id}/status",
                 json=data, headers=auth_header)

    wait_for_scheme_account_status(status, scheme_account_id)
