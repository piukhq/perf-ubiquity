from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TypedDict

    class ClientType(TypedDict):
        bundle_id: str
        client_id: str
        client_name: str
        id: int
        organisation_name: str
        status: int
        whitelist_status: str
        secret: str
        is_trusted: bool


JWT_SECRET = "testsecret"


CLIENT_ONE: "ClientType" = {
    "bundle_id": "performance.bundle.one",
    "client_id": "performance_one",
    "client_name": "performance one",
    "id": 5050,
    "organisation_name": "performance test one",
    "status": 0,
    "whitelist_status": "ACTIVE",
    "secret": JWT_SECRET,
    "is_trusted": False,
}


CLIENT_TWO: "ClientType" = {
    "bundle_id": "performance.bundle.two",
    "client_id": "performance_two",
    "client_name": "performance two",
    "id": 5051,
    "organisation_name": "performance test two",
    "status": 0,
    "whitelist_status": "ACTIVE",
    "secret": JWT_SECRET,
    "is_trusted": False,
}


CLIENT_THREE: "ClientType" = {
    "bundle_id": "performance.bundle.three",
    "client_id": "performance_three",
    "client_name": "performance three",
    "id": 5052,
    "organisation_name": "performance test three",
    "status": 0,
    "whitelist_status": "ACTIVE",
    "secret": JWT_SECRET,
    "is_trusted": False,
}


CLIENT_FOUR: "ClientType" = {
    "bundle_id": "performance.bundle.four",
    "client_id": "performance_four",
    "client_name": "performance four",
    "id": 5053,
    "organisation_name": "performance test four",
    "status": 0,
    "whitelist_status": "ACTIVE",
    "secret": JWT_SECRET,
    "is_trusted": False,
}


CLIENT_FIVE: "ClientType" = {
    "bundle_id": "performance.bundle.five",
    "client_id": "performance_five",
    "client_name": "performance five",
    "id": 5054,
    "organisation_name": "performance test five",
    "status": 0,
    "whitelist_status": "ACTIVE",
    "secret": JWT_SECRET,
    "is_trusted": False,
}


CLIENT_SIX: "ClientType" = {
    "bundle_id": "performance.bundle.six",
    "client_id": "performance_six",
    "client_name": "performance six",
    "id": 5055,
    "organisation_name": "performance test six",
    "status": 0,
    "whitelist_status": "ACTIVE",
    "secret": JWT_SECRET,
    "is_trusted": False,
}


CLIENT_SEVEN: "ClientType" = {
    "bundle_id": "performance.bundle.seven",
    "client_id": "performance_seven",
    "client_name": "performance seven",
    "id": 5056,
    "organisation_name": "performance test seven",
    "status": 0,
    "whitelist_status": "ACTIVE",
    "secret": JWT_SECRET,
    "is_trusted": False,
}


CLIENT_EIGHT: "ClientType" = {
    "bundle_id": "performance.bundle.eight",
    "client_id": "performance_eight",
    "client_name": "performance eight",
    "id": 5057,
    "organisation_name": "performance test eight",
    "status": 0,
    "whitelist_status": "ACTIVE",
    "secret": JWT_SECRET,
    "is_trusted": False,
}


CLIENT_NINE: "ClientType" = {
    "bundle_id": "performance.bundle.nine",
    "client_id": "performance_nine",
    "client_name": "performance nine",
    "id": 5058,
    "organisation_name": "performance test nine",
    "status": 0,
    "whitelist_status": "ACTIVE",
    "secret": JWT_SECRET,
    "is_trusted": False,
}


CLIENT_TEN: "ClientType" = {
    "bundle_id": "performance.bundle.ten",
    "client_id": "performance_ten",
    "client_name": "performance ten",
    "id": 5059,
    "organisation_name": "performance test ten",
    "status": 0,
    "whitelist_status": "ACTIVE",
    "secret": JWT_SECRET,
    "is_trusted": False,
}


CLIENT_ELEVEN: "ClientType" = {
    "bundle_id": "performance.bundle.eleven",
    "client_id": "performance_eleven",
    "client_name": "performance eleven",
    "id": 5060,
    "organisation_name": "performance test eleven",
    "status": 0,
    "whitelist_status": "ACTIVE",
    "secret": JWT_SECRET,
    "is_trusted": False,
}


CLIENT_TWELVE: "ClientType" = {
    "bundle_id": "performance.bundle.twelve",
    "client_id": "performance_twelve",
    "client_name": "performance twelve",
    "id": 5061,
    "organisation_name": "performance test twelve",
    "status": 0,
    "whitelist_status": "ACTIVE",
    "secret": JWT_SECRET,
    "is_trusted": False,
}

CLIENT_RESTRICTED: "ClientType" = {
    "bundle_id": "performance.bundle.restricted",
    "client_id": "performance_restricted",
    "client_name": "performance restricted",
    "id": 5062,
    "organisation_name": "performance test restricted",
    "status": 2,
    "whitelist_status": "INACTIVE",
    "secret": JWT_SECRET,
    "is_trusted": False,
}


CLIENT_TRUSTED_CHANNEL_ONE: "ClientType" = {
    "bundle_id": "performance.bundle.trusted.one",
    "client_id": "performance_trusted_one",
    "client_name": "performance trusted one",
    "id": 5063,
    "organisation_name": "performance test trusted one",
    "status": 0,
    "whitelist_status": "ACTIVE",
    "secret": JWT_SECRET,
    "is_trusted": True,
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
    CLIENT_ELEVEN,
    CLIENT_TWELVE,
]

TRUSTED_CHANNEL_CLIENTS = [CLIENT_TRUSTED_CHANNEL_ONE]

ALL_CLIENTS = [CLIENT_RESTRICTED, *NON_RESTRICTED_CLIENTS, *TRUSTED_CHANNEL_CLIENTS]
