import logging
import time

import requests

from data_population.fixtures.client import CLIENT_ONE
from request_data import service
from settings import HERMES_URL

logger = logging.getLogger(__name__)


def slow_retry_request(method: str, url: str, headers: dict, json: dict = None, params: dict = None):
    for _ in range(10):
        try:
            logger.debug("Attempting setup requests to Hermes to get information like membership_plan total...")
            resp = requests.request(method, url, headers=headers, json=json, params=params)
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            logger.debug(f"Setup request failed due to: {repr(e)}, trying again in 30 seconds...")
            time.sleep(30)
            pass

    raise RuntimeError(
        "Locust failed to start due to a requests failure which locust runs on startup"
        "to get some setup information e.g. membership_plan total. Please make sure data population is "
        "run to make sure the right clients are set up, and the Hermes pods are running fine"
    )


def request_membership_plan_total():
    if not HERMES_URL:
        logger.debug("No HERMES_URL environment variable set, skipping membership plan total setup")
        return 7

    email = "performance-test@bink.com"
    timestamp = int(time.time())

    headers = service.generate_auth_header(email, timestamp, CLIENT_ONE, CLIENT_ONE["secret"])
    body = service.generate_setup_user()
    service_url = f"{HERMES_URL}/ubiquity/service"
    slow_retry_request("POST", service_url, headers, json=body)

    params = {"fields": "id"}
    plan_url = f"{HERMES_URL}/ubiquity/membership_plans"
    resp = slow_retry_request("GET", plan_url, headers, params=params)
    membership_plan_total = len(resp.json())

    logger.debug(
        "Obtained membership plan total from ubiquity, "
        f"setting number of membership plans to use in tests to: {membership_plan_total}"
    )
    return membership_plan_total
