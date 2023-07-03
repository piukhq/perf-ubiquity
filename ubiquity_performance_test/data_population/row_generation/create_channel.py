from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ubiquity_performance_test.data_population.fixtures.client import ClientType


def organisation(fixture: "ClientType") -> list:
    return [fixture["id"], fixture["organisation_name"], "organisation terms and conditions"]


def client_application(fixture: "ClientType") -> list:
    return [fixture["client_id"], fixture["client_name"], fixture["id"], fixture["secret"]]


def client_application_bundle(fixture: "ClientType") -> list:
    return [
        fixture["id"],  # id
        fixture["bundle_id"],  # bundle_id
        fixture["client_id"],  # client_id
        60,  # magic_lifetime
        "",  # magic_link_url
        "",  # external_name
        "",  # email_from
        "",  # subject
        "",  # template
        10,  # access_token_lifetime
        15,  # refresh_token_lifetime
        False,  # email_required
        fixture["is_trusted"],  # is_trusted
    ]


def channel_scheme_whitelist(whitelist_id: int, fixture: "ClientType", scheme_id: int) -> list:
    return [whitelist_id, fixture["status"], fixture["id"], scheme_id, False]  # test scheme
