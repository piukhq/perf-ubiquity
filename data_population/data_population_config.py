from dataclasses import dataclass


@dataclass
class DataConfig:
    name: str
    membership_plans: int
    users: int
    membership_cards: int
    payment_cards: int
    transactions: int


test = DataConfig(
    name="test",
    membership_plans=7,
    users=500,
    membership_cards=5000,
    payment_cards=2000,
    transactions=10000
)


benchmark = DataConfig(
    name="benchmark",
    membership_plans=7,
    users=449333,
    membership_cards=3082426,
    payment_cards=674000,
    transactions=30824266
)


barclays_2021 = DataConfig(
    name="barclays_2021",
    membership_plans=18,
    users=5392000,
    membership_cards=36989120,
    payment_cards=8088000,
    transactions=369891200
)


barclays_2022 = DataConfig(
    name="barclays_2022",
    membership_plans=26,
    users=8192000,
    membership_cards=56197120,
    payment_cards=12288000,
    transactions=561971200
)


barclays_2023 = DataConfig(
    name="barclays_2023",
    membership_plans=35,
    users=11011000,
    membership_cards=75535460,
    payment_cards=16516500,
    transactions=755354600
)


barclays_2024 = DataConfig(
    name="barclays_2024",
    membership_plans=50,
    users=13593000,
    membership_cards=93247980,
    payment_cards=20389500,
    transactions=932479800
)


barclays_internal_test = DataConfig(
    name="barclays_internal_test",
    membership_plans=3,
    users=5000,
    membership_cards=5000,
    payment_cards=2000,
    transactions=10000
)

all_configs = [test, benchmark, barclays_2021, barclays_2022, barclays_2023, barclays_2024, barclays_internal_test]
all_config_names = [config.name for config in all_configs]
