CLIENT_ONE = {
    'bundle_id': 'performance.bundle.one',
    'client_id': 'performance_one',
    'client_name': 'performance one',
    'id': 5050,
    'organisation_name': 'performance test one',
    'status': 0,
    'whitelist_status': 'ACTIVE',
    "secret": "testsecret",
}


CLIENT_TWO = {
    'bundle_id': 'performance.bundle.two',
    'client_id': 'performance_two',
    'client_name': 'performance two',
    'id': 5051,
    'organisation_name': 'performance test two',
    'status': 0,
    'whitelist_status': 'ACTIVE',
    "secret": "testsecret",
}


CLIENT_THREE = {
    'bundle_id': 'performance.bundle.three',
    'client_id': 'performance_three',
    'client_name': 'performance three',
    'id': 5052,
    'organisation_name': 'performance test three',
    'status': 0,
    'whitelist_status': 'ACTIVE',
    "secret": "testsecret",
}


CLIENT_FOUR = {
    'bundle_id': 'performance.bundle.four',
    'client_id': 'performance_four',
    'client_name': 'performance four',
    'id': 5053,
    'organisation_name': 'performance test four',
    'status': 0,
    'whitelist_status': 'ACTIVE',
    "secret": "testsecret",
}


CLIENT_FIVE = {
    'bundle_id': 'performance.bundle.five',
    'client_id': 'performance_five',
    'client_name': 'performance five',
    'id': 5054,
    'organisation_name': 'performance test five',
    'status': 0,
    'whitelist_status': 'ACTIVE',
    "secret": "testsecret",
}


CLIENT_SIX = {
    'bundle_id': 'performance.bundle.six',
    'client_id': 'performance_six',
    'client_name': 'performance six',
    'id': 5055,
    'organisation_name': 'performance test six',
    'status': 0,
    'whitelist_status': 'ACTIVE',
    "secret": "testsecret",
}


CLIENT_SEVEN = {
    'bundle_id': 'performance.bundle.seven',
    'client_id': 'performance_seven',
    'client_name': 'performance seven',
    'id': 5056,
    'organisation_name': 'performance test seven',
    'status': 0,
    'whitelist_status': 'ACTIVE',
    "secret": "testsecret",
}


CLIENT_EIGHT = {
    'bundle_id': 'performance.bundle.eight',
    'client_id': 'performance_eight',
    'client_name': 'performance eight',
    'id': 5057,
    'organisation_name': 'performance test eight',
    'status': 0,
    'whitelist_status': 'ACTIVE',
    "secret": "testsecret",
}


CLIENT_NINE = {
    'bundle_id': 'performance.bundle.nine',
    'client_id': 'performance_nine',
    'client_name': 'performance nine',
    'id': 5058,
    'organisation_name': 'performance test nine',
    'status': 0,
    'whitelist_status': 'ACTIVE',
    "secret": "testsecret",
}


CLIENT_TEN = {
    'bundle_id': 'performance.bundle.ten',
    'client_id': 'performance_ten',
    'client_name': 'performance ten',
    'id': 5059,
    'organisation_name': 'performance test ten',
    'status': 0,
    'whitelist_status': 'ACTIVE',
    "secret": "testsecret",
}


CLIENT_ELEVEN = {
    'bundle_id': 'performance.bundle.eleven',
    'client_id': 'performance_eleven',
    'client_name': 'performance eleven',
    'id': 5060,
    'organisation_name': 'performance test eleven',
    'status': 0,
    'whitelist_status': 'ACTIVE',
    "secret": "testsecret",
}

CLIENT_RESTRICTED = {
    "bundle_id": "performance.bundle.restricted",
    "client_id": "performance_restricted",
    "client_name": "performance restricted",
    "id": 5061,
    "organisation_name": "performance test restricted",
    "status": 2,
    "whitelist_status": "INACTIVE",
    "secret": "testsecret",
}

NON_RESTRICTED_CLIENTS = [
    CLIENT_ONE,
    CLIENT_TWO,
    CLIENT_THREE,
    CLIENT_FOUR,
    CLIENT_FIVE,
    CLIENT_SIX,
    CLIENT_SEVEN,
    CLIENT_EIGHT,
    CLIENT_NINE,
    CLIENT_TEN,
    CLIENT_ELEVEN
]
ALL_CLIENTS = [CLIENT_RESTRICTED] + NON_RESTRICTED_CLIENTS
