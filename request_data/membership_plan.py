from enum import Enum, IntEnum


class PlanIDs(IntEnum):
    ICELAND = 105
    HARVEY_NICHOLS = 194
    COOP = 242
    TEST_SCHEME_ID = 5050


class ClientIDs(IntEnum):
    BARCLAYS = 2


class ClientBundleIDs(str, Enum):
    BARCLAYS = "com.barclays.test"
