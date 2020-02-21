STATIC_START_ID = 50000

MEMBERSHIP_PLANS = 40
MEMBERSHIP_PLAN_IDS = [x for x in range(STATIC_START_ID, STATIC_START_ID + MEMBERSHIP_PLANS)]

CLIENT_ONE = {
    "client_id": "performance_one",
    "client_name": "performance one",
    "secret": "testsecret",
    "id": 5050,
    "organisation_name": "performance test one",
    "organisation_t_and_c": "one",
    "bundle_id": "performance_bundle_one",
    "status": 0,
    "daedalus_status": "ACTIVE",
}


CLIENT_TWO = {
    "client_id": "performance_two",
    "client_name": "performance two",
    "secret": "testsecret",
    "id": 5051,
    "organisation_name": "performance test two",
    "organisation_t_and_c": "one",
    "bundle_id": "performance_bundle_two",
    "status": 0,
    "daedalus_status": "ACTIVE",
}


CLIENT_RESTRICTED = {
    "client_id": "performance_restricted",
    "client_name": "performance restricted",
    "secret": "testsecret",
    "id": 5052,
    "organisation_name": "performance test restricted",
    "organisation_t_and_c": "one",
    "bundle_id": "performance_bundle_restricted",
    "status": 2,
    "daedalus_status": "INACTIVE",
}
