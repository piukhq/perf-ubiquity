import random
import jwt
import datetime

from locust import HttpUser, SequentialTaskSet, constant, task
from locust.exception import StopUser
from requests import codes

from data_population.fixtures.client import CLIENT_ONE, CLIENT_RESTRICTED, NON_RESTRICTED_CLIENTS
from locust_config import (
    AUTOLINK,
    MEMBERSHIP_PLANS,
    MULTIPLE_PROPERTY_PCARD_INDEX,
    NON_PATCH_PLANS,
    PATCH_PLANS,
    TOTAL_CLIENTS,
    LocustLabel,
    check_suite_whitelist,
    increment_locust_counter,
    repeat_task,
)
from request_data import angelia, membership_card, payment_card, service
from request_data.hermes import post_scheme_account_status, wait_for_scheme_account_status
from vault import load_secrets


class UserBehavior(SequentialTaskSet):
    def __init__(self, parent):
        self.email, self.external_id = angelia.generate_random_email_and_sub()
        self.single_prop_header = {}
        self.multi_prop_header = {}
        self.restricted_prop_header = {}
        self.non_restricted_auth_headers = {}
        self.enumerated_patch_users = []
        self.all_auth_headers = []
        self.membership_plan_total = MEMBERSHIP_PLANS
        self.payment_cards = []
        self.membership_cards = []
        self.join_membership_cards = []
        self.ghost_cards = []
        self.service_counter = 0
        self.plan_counter = 1
        self.client_secrets = load_secrets()
        self.pub_key = self.client_secrets[CLIENT_ONE["bundle_id"]]["public_key"]
        self.private_key = self.client_secrets[CLIENT_ONE["bundle_id"]]["private_key"]
        self.url_prefix = "/v2"
        super(UserBehavior, self).__init__(parent)

    @task
    def setup_headers(self):
        if not self.pub_key:
            self.client_secrets = load_secrets()
            self.pub_key = self.client_secrets[CLIENT_ONE["bundle_id"]]["public_key"]

        self.plan_counter = 1
        self.payment_cards = []
        self.membership_cards = []
        self.join_membership_cards = []
        self.ghost_cards = []
        email = self.consent["consent"]["email"]
        timestamp = self.consent["consent"]["timestamp"]

        single_prop_jwt_secret = self.client_secrets[CLIENT_ONE["bundle_id"]]["jwt_secret"]
        self.single_prop_header = service.generate_auth_header(email, timestamp, CLIENT_ONE, single_prop_jwt_secret)
        multi_prop_channel = random.choice(NON_RESTRICTED_CLIENTS[1: TOTAL_CLIENTS - 1])
        multi_prop_jwt_secret = self.client_secrets[multi_prop_channel["bundle_id"]]["jwt_secret"]
        self.multi_prop_header = service.generate_auth_header(
            email, timestamp, multi_prop_channel, multi_prop_jwt_secret
        )

        restricted_jwt_secret = self.client_secrets[CLIENT_RESTRICTED["bundle_id"]]["jwt_secret"]
        self.restricted_prop_header = service.generate_auth_header(
            email, timestamp, CLIENT_RESTRICTED, restricted_jwt_secret
        )
        self.non_restricted_auth_headers = {
            LocustLabel.SINGLE_PROPERTY: self.single_prop_header,
            LocustLabel.MULTI_PROPERTY: self.multi_prop_header,
        }
        self.enumerated_patch_users = list(enumerate([self.single_prop_header, self.multi_prop_header]))
        self.all_auth_headers = [self.single_prop_header, self.multi_prop_header, self.restricted_prop_header]

    def generate_b2b_token(self):
        access_life_time = 400
        iat = datetime.datetime.utcnow()
        exp = iat + datetime.timedelta(seconds=access_life_time)

        payload = {"email": "", "sub": "", "iat": iat, "exp": exp}
        headers = {"kid": "bundle.performance.one"}  # todo: Add KID with keys to Azure KeyVault
        key = self.private_key

        b2b_token = jwt.encode(payload=payload, key=key, algorithm='RS512', headers=headers)

    @task
    def post_token(self):
        self.client.post(
            f"{self.url_prefix}/token", json=self.consent, headers=">>AUTH HEADER<<", name=f"{self.url_prefix}/token"
        )