import random
from typing import TYPE_CHECKING

from locust import HttpUser, SequentialTaskSet, constant, task
from requests import codes

from ubiquity_performance_test.data_population.fixtures.client import (
    CLIENT_ONE,
    CLIENT_RESTRICTED,
    NON_RESTRICTED_CLIENTS,
)
from ubiquity_performance_test.locust_angelia.database.jobs import set_status_for_loyalty_card
from ubiquity_performance_test.locust_config import (
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
from ubiquity_performance_test.request_data import membership_card, payment_card, service
from ubiquity_performance_test.request_data.hermes import wait_for_scheme_account_status
from ubiquity_performance_test.vault import vault_secrets

if TYPE_CHECKING:
    from ubiquity_performance_test.request_data.service import ConsentType


class UserBehavior(SequentialTaskSet):
    def __init__(self, parent: type[SequentialTaskSet]) -> None:
        self.consent: "ConsentType" = {}
        self.single_prop_header: dict = {}
        self.multi_prop_header: dict = {}
        self.restricted_prop_header: dict = {}
        self.non_restricted_auth_headers: dict = {}
        self.enumerated_patch_users: list = []
        self.all_auth_headers: list = []
        self.membership_plan_total = MEMBERSHIP_PLANS
        self.payment_cards: list = []
        self.membership_cards: list = []
        self.join_membership_cards: list = []
        self.ghost_cards: list = []
        self.service_counter = 0
        self.plan_counter = 1
        self.client_secrets = vault_secrets.channel_info["channel_secrets"]
        self.pub_key = self.client_secrets[CLIENT_ONE["bundle_id"]]["public_key"]
        self.url_prefix = "/ubiquity"
        super().__init__(parent)

    @task
    def setup_headers(self) -> None:
        if not self.pub_key:
            self.client_secrets = vault_secrets.channel_info
            self.pub_key = self.client_secrets[CLIENT_ONE["bundle_id"]]["public_key"]

        self.plan_counter = 1
        self.payment_cards = []
        self.membership_cards = []
        self.join_membership_cards = []
        self.ghost_cards = []
        self.consent = service.generate_random()
        email = self.consent["consent"]["email"]
        timestamp = self.consent["consent"]["timestamp"]

        single_prop_jwt_secret = self.client_secrets[CLIENT_ONE["bundle_id"]]["jwt_secret"]
        self.single_prop_header = service.generate_auth_header(email, timestamp, CLIENT_ONE, single_prop_jwt_secret)
        multi_prop_channel = random.choice(NON_RESTRICTED_CLIENTS[1 : TOTAL_CLIENTS - 1])
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

    @task
    def post_service(self) -> None:
        for auth_header in self.all_auth_headers:
            self.client.post(
                f"{self.url_prefix}/service",
                json=self.consent,
                headers=auth_header,
                name=f"{self.url_prefix}/service {LocustLabel.SINGLE_PROPERTY}",
            )

    @check_suite_whitelist
    @task
    @repeat_task(2)
    def get_service(self) -> None:
        for auth_header in self.all_auth_headers:
            self.client.get(
                f"{self.url_prefix}/service",
                headers=auth_header,
                name=f"{self.url_prefix}/service {LocustLabel.SINGLE_PROPERTY}",
            )

    @check_suite_whitelist
    @task
    @repeat_task(5)
    def post_membership_cards_single_property_join(self) -> None:
        plan_id = self.plan_counter
        mcard_json = membership_card.random_join_json(plan_id, self.pub_key)
        self.plan_counter = increment_locust_counter(self.plan_counter, len(NON_PATCH_PLANS))

        with self.client.post(
            f"{self.url_prefix}/membership_cards",
            params=AUTOLINK,
            json=mcard_json,
            headers=self.restricted_prop_header,
            name=f"{self.url_prefix}/membership_cards {LocustLabel.SINGLE_RESTRICTED_PROPERTY}",
            catch_response=True,
        ) as response:
            if response.status_code == codes.BAD_REQUEST:
                response.success()

        resp = self.client.post(
            f"{self.url_prefix}/membership_cards",
            json=mcard_json,
            headers=self.single_prop_header,
            name=f"{self.url_prefix}/membership_cards {LocustLabel.SINGLE_PROPERTY}",
        )

        mcard = {"id": resp.json()["id"], "plan_id": plan_id, "json": mcard_json}
        self.join_membership_cards.append(mcard)

    @check_suite_whitelist
    @task
    @repeat_task(6)
    def get_membership_plans(self) -> None:
        plan_filters = {
            "fields": ["id", "status", "feature_set", "account", "images", "balances", "card", "content"],
        }
        resp = self.client.get(
            f"{self.url_prefix}/membership_plans",
            params=plan_filters,
            headers=self.single_prop_header,
            name=f"{self.url_prefix}/membership_plans {LocustLabel.SINGLE_PROPERTY}",
        )

        self.membership_plan_total = len(resp.json())

    @check_suite_whitelist
    @task
    @repeat_task(24)
    def get_membership_plan_id(self) -> None:
        plan_id = random.choice(range(1, self.membership_plan_total))
        self.client.get(
            f"{self.url_prefix}/membership_plan/{plan_id}",
            headers=self.single_prop_header,
            name=f"{self.url_prefix}/membership_plan/<plan_id> {LocustLabel.SINGLE_PROPERTY}",
        )

    @check_suite_whitelist
    @task
    @repeat_task(2)
    def post_membership_cards_single_property_add(self) -> None:
        plan_id = self.plan_counter
        mcard_json = membership_card.random_add_json(plan_id, self.pub_key)
        self.plan_counter = increment_locust_counter(self.plan_counter, len(NON_PATCH_PLANS))
        with self.client.post(
            f"{self.url_prefix}/membership_cards",
            params=AUTOLINK,
            json=mcard_json,
            headers=self.restricted_prop_header,
            name=f"{self.url_prefix}/membership_cards {LocustLabel.SINGLE_RESTRICTED_PROPERTY}",
            catch_response=True,
        ) as response:
            if response.status_code == codes.BAD_REQUEST:
                response.success()

        resp = self.client.post(
            f"{self.url_prefix}/membership_cards",
            params=AUTOLINK,
            json=mcard_json,
            headers=self.single_prop_header,
            name=f"{self.url_prefix}/membership_cards {LocustLabel.SINGLE_PROPERTY}",
        )

        mcard = {"id": resp.json()["id"], "plan_id": plan_id, "json": mcard_json}
        self.membership_cards.append(mcard)

    @check_suite_whitelist
    @task
    def post_membership_cards_single_property_add_ghost_cards(self) -> None:
        for count, auth_header in self.enumerated_patch_users:
            plan_id = PATCH_PLANS[count]
            mcard_json = membership_card.random_add_ghost_card_json(plan_id, self.pub_key)
            with self.client.post(
                f"{self.url_prefix}/membership_cards",
                params=AUTOLINK,
                json=mcard_json,
                headers=self.restricted_prop_header,
                name=f"{self.url_prefix}/membership_cards {LocustLabel.SINGLE_RESTRICTED_PROPERTY}",
                catch_response=True,
            ) as response:
                if response.status_code == codes.BAD_REQUEST:
                    response.success()

            resp = self.client.post(
                f"{self.url_prefix}/membership_cards",
                params=AUTOLINK,
                json=mcard_json,
                headers=auth_header,
                name=f"{self.url_prefix}/membership_cards {LocustLabel.SINGLE_PROPERTY}",
            )

            mcard = {"id": resp.json()["id"], "plan_id": plan_id, "json": mcard_json}
            self.ghost_cards.append(mcard)

    @check_suite_whitelist
    @task
    @repeat_task(5)
    def post_payment_cards_single_property(self) -> None:
        pcard = payment_card.generate_unencrypted_random()
        pcard_hash = pcard["card"]["hash"]
        pcard_json = payment_card.encrypt(pcard, self.pub_key)
        resp = self.client.post(
            f"{self.url_prefix}/payment_cards",
            params=AUTOLINK,
            json=pcard_json,
            headers=self.single_prop_header,
            name=f"{self.url_prefix}/payment_cards {LocustLabel.SINGLE_PROPERTY}",
        )

        pcard_id = resp.json()["id"]
        pcard = {"id": pcard_id, "hash": pcard_hash, "json": pcard_json}
        self.payment_cards.append(pcard)

    @check_suite_whitelist
    @task
    def post_payment_cards_multiple_property(self) -> None:
        pcard_json = self.payment_cards[MULTIPLE_PROPERTY_PCARD_INDEX]["json"]
        self.client.post(
            f"{self.url_prefix}/payment_cards",
            params=AUTOLINK,
            json=pcard_json,
            headers=self.multi_prop_header,
            name=f"{self.url_prefix}/payment_cards {LocustLabel.MULTI_PROPERTY}",
        )

    @check_suite_whitelist
    @task
    @repeat_task(3)
    def get_membership_card_single_property(self) -> None:
        for mcard in self.membership_cards:
            self.client.get(
                f"{self.url_prefix}/membership_card/{mcard['id']}",
                headers=self.single_prop_header,
                name=f"{self.url_prefix}/membership_card/<card_id> {LocustLabel.SINGLE_PROPERTY}",
            )

        for count, auth_header in self.enumerated_patch_users:
            mcard = self.ghost_cards[count]
            self.client.get(
                f"{self.url_prefix}/membership_card/{mcard['id']}",
                headers=auth_header,
                name=f"{self.url_prefix}/membership_card/<card_id> {LocustLabel.SINGLE_PROPERTY}",
            )

    @check_suite_whitelist
    @task
    @repeat_task(3)
    def get_membership_card_transactions_single_property(self) -> None:
        for mcard in self.membership_cards:
            self.client.get(
                f"{self.url_prefix}/membership_card/{mcard['id']}/membership_transactions",
                headers=self.single_prop_header,
                name=f"{self.url_prefix}/membership_card/<card_id>/membership_transactions"
                f" {LocustLabel.SINGLE_PROPERTY}",
            )

        for count, auth_header in self.enumerated_patch_users:
            mcard = self.ghost_cards[count]
            self.client.get(
                f"{self.url_prefix}/membership_card/{mcard['id']}/membership_transactions",
                headers=auth_header,
                name=f"{self.url_prefix}/membership_card/<card_id>/membership_transactions"
                f" {LocustLabel.SINGLE_PROPERTY}",
            )

    @check_suite_whitelist
    @task
    def patch_membership_card_id_payment_card_id_single_property(self) -> None:
        pcard_id = self.payment_cards[1]["id"]
        mcard_id = self.membership_cards[0]["id"]
        self.client.patch(
            f"{self.url_prefix}/membership_card/{mcard_id}/payment_card/{pcard_id}",
            headers=self.single_prop_header,
            name=f"{self.url_prefix}/membership_card/<mcard_id>/payment_card/<pcard_id> "
            f""
            f"{LocustLabel.SINGLE_PROPERTY}",
        )

        with self.client.patch(
            f"{self.url_prefix}/membership_card/{mcard_id}/payment_card/{pcard_id}",
            headers=self.restricted_prop_header,
            catch_response=True,
            name=f"{self.url_prefix}/membership_card/<mcard_id>/payment_card/<pcard_id> "
            f""
            f"{LocustLabel.SINGLE_RESTRICTED_PROPERTY}",
        ) as response:
            if response.status_code == codes.NOT_FOUND:
                response.success()

    @check_suite_whitelist
    @task
    def patch_payment_card_id_membership_card_id_single_property(self) -> None:
        pcard_id = self.payment_cards[1]["id"]
        mcard_id = self.membership_cards[1]["id"]
        self.client.patch(
            f"{self.url_prefix}/payment_card/{pcard_id}/membership_card/{mcard_id}",
            headers=self.single_prop_header,
            name=f"{self.url_prefix}/payment_card/<pcard_id>/membership_card/<mcard_id> "
            f""
            f"{LocustLabel.SINGLE_PROPERTY}",
        )

        with self.client.patch(
            f"{self.url_prefix}/payment_card/{pcard_id}/membership_card/{mcard_id}",
            headers=self.restricted_prop_header,
            catch_response=True,
            name=f"{self.url_prefix}/payment_card/<pcard_id>/membership_card/<mcard_id> "
            f""
            f"{LocustLabel.SINGLE_RESTRICTED_PROPERTY}",
        ) as response:
            if response.status_code == codes.NOT_FOUND:
                response.success()

    @check_suite_whitelist
    @task
    def post_membership_cards_multiple_property_restricted(self) -> None:
        all_restricted_cards = self.membership_cards + self.ghost_cards
        for mcard in all_restricted_cards:
            with self.client.post(
                f"{self.url_prefix}/membership_cards",
                params=AUTOLINK,
                json=mcard["json"],
                headers=self.restricted_prop_header,
                name=f"{self.url_prefix}/membership_cards {LocustLabel.MULTI_RESTRICTED_PROPERTY}",
                catch_response=True,
            ) as response:
                if response.status_code == codes.BAD_REQUEST:
                    response.success()

    @check_suite_whitelist
    @task
    def post_membership_cards_multiple_property(self) -> None:
        multi_property_error = (
            "Multi-property membership card request created brand new card rather than " "linking to existing card"
        )
        for mcard in self.membership_cards:
            with self.client.post(
                f"{self.url_prefix}/membership_cards",
                params=AUTOLINK,
                json=mcard["json"],
                headers=self.multi_prop_header,
                catch_response=True,
                name=f"{self.url_prefix}/membership_cards {LocustLabel.MULTI_PROPERTY}",
            ) as response:
                new_mcard_id = response.json()["id"]
                if new_mcard_id == mcard["id"]:
                    response.success()
                else:
                    response.failure(multi_property_error)

        for count, auth_header in enumerate([self.multi_prop_header, self.single_prop_header]):
            mcard = self.ghost_cards[count]
            with self.client.post(
                f"{self.url_prefix}/membership_cards",
                params=AUTOLINK,
                json=mcard["json"],
                headers=auth_header,
                catch_response=True,
                name=f"{self.url_prefix}/membership_cards {LocustLabel.MULTI_PROPERTY}",
            ) as response:
                new_mcard_id = response.json()["id"]
                if new_mcard_id == mcard["id"]:
                    response.success()
                else:
                    response.failure(multi_property_error)

    @check_suite_whitelist
    @task
    def patch_membership_card_id_payment_card_id_multiple_property(self) -> None:
        pcard_id = self.payment_cards[MULTIPLE_PROPERTY_PCARD_INDEX]["id"]
        mcard_id = self.membership_cards[0]["id"]
        self.client.patch(
            f"{self.url_prefix}/membership_card/{mcard_id}/payment_card/{pcard_id}",
            headers=self.multi_prop_header,
            name=f"{self.url_prefix}/membership_card/<mcard_id>/payment_card/<pcard_id> "
            f""
            f"{LocustLabel.MULTI_PROPERTY}",
        )

        with self.client.patch(
            f"{self.url_prefix}/membership_card/{mcard_id}/payment_card/{pcard_id}",
            headers=self.restricted_prop_header,
            catch_response=True,
            name=f"{self.url_prefix}/membership_card/<mcard_id>/payment_card/<pcard_id> "
            f""
            f"{LocustLabel.MULTI_RESTRICTED_PROPERTY}",
        ) as response:
            if response.status_code == codes.NOT_FOUND:
                response.success()

    @check_suite_whitelist
    @task
    def patch_payment_card_id_membership_card_id_multiple_property(self) -> None:
        pcard_id = self.payment_cards[MULTIPLE_PROPERTY_PCARD_INDEX]["id"]
        mcard_id = self.membership_cards[1]["id"]
        self.client.patch(
            f"{self.url_prefix}/payment_card/{pcard_id}/membership_card/{mcard_id}",
            headers=self.multi_prop_header,
            name=f"{self.url_prefix}/payment_card/<pcard_id>/membership_card/<mcard_id> "
            f""
            f"{LocustLabel.MULTI_PROPERTY}",
        )

        with self.client.patch(
            f"{self.url_prefix}/payment_card/{pcard_id}/membership_card/{mcard_id}",
            headers=self.restricted_prop_header,
            catch_response=True,
            name=f"{self.url_prefix}/payment_card/<pcard_id>/membership_card/<mcard_id> "
            f""
            f"{LocustLabel.MULTI_RESTRICTED_PROPERTY}",
        ) as response:
            if response.status_code == codes.NOT_FOUND:
                response.success()

    @check_suite_whitelist
    @task
    @repeat_task(2)
    def get_membership_card_multiple_property(self) -> None:
        all_multi_property_cards = self.membership_cards + self.ghost_cards
        for mcard in all_multi_property_cards:
            self.client.get(
                f"{self.url_prefix}/membership_card/{mcard['id']}",
                headers=self.multi_prop_header,
                name=f"{self.url_prefix}/membership_card/<card_id> {LocustLabel.MULTI_PROPERTY}",
            )

    @check_suite_whitelist
    @task
    @repeat_task(2)
    def get_membership_card_transactions_multiple_property(self) -> None:
        all_multi_property_cards = self.membership_cards + self.ghost_cards
        for mcard in all_multi_property_cards:
            self.client.get(
                f"{self.url_prefix}/membership_card/{mcard['id']}/membership_transactions",
                headers=self.multi_prop_header,
                name=f"{self.url_prefix}/membership_card/<card_id>/membership_transactions "
                f"{LocustLabel.MULTI_PROPERTY}",
            )

    @check_suite_whitelist
    @task
    @repeat_task(27)
    def get_payment_cards(self) -> None:
        for auth_header in self.non_restricted_auth_headers.values():
            self.client.get(
                f"{self.url_prefix}/payment_cards",
                headers=auth_header,
                name=f"{self.url_prefix}/payment_cards {LocustLabel.SINGLE_PROPERTY}",
            )

    @check_suite_whitelist
    @task
    @repeat_task(27)
    def get_membership_cards(self) -> None:
        mcard_filters = {
            "fields": [
                "id",
                "membership_plan",
                "status",
                "payment_cards",
                "card",
                "account",
                "balances",
                "images",
                "voucher",
            ],
        }
        for auth_header in self.non_restricted_auth_headers.values():
            self.client.get(
                f"{self.url_prefix}/membership_cards",
                params=mcard_filters,
                headers=auth_header,
                name=f"{self.url_prefix}/membership_cards {LocustLabel.SINGLE_PROPERTY}",
            )

    @check_suite_whitelist
    @task
    def patch_membership_cards_id_ghost(self) -> None:
        for count, auth_header in self.enumerated_patch_users:
            mcard_id = self.ghost_cards[count]["id"]
            mcard_json = membership_card.random_registration_json(self.pub_key)

            updated = wait_for_scheme_account_status(membership_card.PRE_REGISTERED_CARD_STATUS, mcard_id)
            if not updated:
                set_status_for_loyalty_card(mcard_id, membership_card.PRE_REGISTERED_CARD_STATUS)
            self.client.patch(
                f"{self.url_prefix}/membership_card/{mcard_id}",
                json=mcard_json,
                headers=auth_header,
                name=f"{self.url_prefix}/membership_card/<mcard_id> {LocustLabel.SINGLE_PROPERTY}",
            )

    @check_suite_whitelist
    @task
    def patch_membership_cards_id_add(self) -> None:
        task_counter = 3
        for x in range(task_counter):
            # reset index if range > max number of membership cards
            converted_index = x % len(self.join_membership_cards)
            mcard_id = self.join_membership_cards[converted_index]["id"]
            mcard_json = membership_card.random_patch_json(self.pub_key)
            self.client.patch(
                f"{self.url_prefix}/membership_card/{mcard_id}",
                json=mcard_json,
                headers=self.single_prop_header,
                name=f"{self.url_prefix}/membership_card/<mcard_id> {LocustLabel.SINGLE_PROPERTY}",
            )

    @check_suite_whitelist
    @task
    def delete_payment_card_multiple_property(self) -> None:
        pcard_id = self.payment_cards[MULTIPLE_PROPERTY_PCARD_INDEX]["id"]
        self.client.delete(
            f"{self.url_prefix}/payment_card/{pcard_id}",
            headers=self.multi_prop_header,
            name=f"{self.url_prefix}/payment_card/<card_id> {LocustLabel.MULTI_PROPERTY}",
        )

    @check_suite_whitelist
    @task
    @repeat_task(3)
    def delete_payment_card_single_property(self) -> None:
        pcard_id = self.payment_cards.pop(0)["id"]
        self.client.delete(
            f"{self.url_prefix}/payment_card/{pcard_id}",
            headers=self.single_prop_header,
            name=f"{self.url_prefix}/payment_card/<card_id> {LocustLabel.SINGLE_PROPERTY}",
        )

    @check_suite_whitelist
    @task
    def delete_payment_card_by_hash_multiple_property(self) -> None:
        hash_val = self.payment_cards[MULTIPLE_PROPERTY_PCARD_INDEX]["hash"]
        self.client.delete(
            f"{self.url_prefix}/payment_card/hash-{hash_val}",
            headers=self.multi_prop_header,
            name=f"{self.url_prefix}/payment_card/hash-<hash> {LocustLabel.MULTI_PROPERTY}",
        )

    @check_suite_whitelist
    @task
    @repeat_task(3)
    def delete_payment_card_by_hash_single_property(self) -> None:
        hash_val = self.payment_cards.pop(0)["hash"]
        self.client.delete(
            f"{self.url_prefix}/payment_card/hash-{hash_val}",
            headers=self.single_prop_header,
            name=f"{self.url_prefix}/payment_card/hash-<hash> {LocustLabel.SINGLE_PROPERTY}",
        )

    @check_suite_whitelist
    @task
    @repeat_task(2)
    def delete_membership_card(self) -> None:
        mcard = self.membership_cards.pop(0)
        self.client.delete(
            f"{self.url_prefix}/membership_card/{mcard['id']}",
            headers=self.multi_prop_header,
            name=f"{self.url_prefix}/membership_card/<card_id> {LocustLabel.MULTI_PROPERTY}",
        )

        self.client.delete(
            f"{self.url_prefix}/membership_card/{mcard['id']}",
            headers=self.single_prop_header,
            name=f"{self.url_prefix}/membership_card/<card_id> {LocustLabel.SINGLE_PROPERTY}",
        )

    @check_suite_whitelist
    @task
    def delete_service(self) -> None:
        if self.service_counter % 10 == 0:
            for auth_header in self.all_auth_headers:
                self.client.delete(
                    f"{self.url_prefix}/service",
                    headers=auth_header,
                    name=f"{self.url_prefix}/service {LocustLabel.SINGLE_PROPERTY}",
                )

        self.service_counter += 1


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]  # noqa: RUF012
    wait_time = constant(0.5)
