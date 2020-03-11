def organisation(fixture):
    return [fixture['id'], fixture['organisation_name'], "organisation terms and conditions"]


def client_application(fixture):
    return [fixture['client_id'], fixture['client_name'], fixture['id'], fixture['secret']]


def client_application_bundle(fixture):
    return [fixture['id'], fixture['bundle_id'], fixture['client_id']]


def channel_scheme_whitelist(whitelist_id, fixture, scheme_id):
    return [whitelist_id, fixture['status'], fixture['id'], scheme_id]