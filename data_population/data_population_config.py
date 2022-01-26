from dataclasses import dataclass


@dataclass
class DataConfig:
    name: str
    membership_plans: int
    users: int
    users_history: int
    membership_cards: int
    membership_cards_history: int
    payment_cards: int
    payment_cards_history: int
    transactions: int


test = DataConfig(
    name="test",
    membership_plans=7,
    users=500,
    users_history=600,
    membership_cards=5000,
    membership_cards_history=6000,
    payment_cards=2000,
    payment_cards_history=3000,
    transactions=10000,
)


benchmark_old = DataConfig(
    name="benchmark",
    membership_plans=7,
    users=449333,
    users_history=449333,
    membership_cards=3082426,
    membership_cards_history=3082426,
    payment_cards=674000,
    payment_cards_history=674000,
    transactions=30824266,
)


benchmark = DataConfig(
    name="benchmark",
    membership_plans=36,
    users=273500,
    users_history=547000,
    membership_cards=1876210,
    membership_cards_history=7493900,
    payment_cards=410250,
    payment_cards_history=615375,
    transactions=6153750,
)


barclays_2021_old = DataConfig(
    name="barclays_2021",
    membership_plans=18,
    users=5392000,
    users_history=5392000,
    membership_cards=36989120,
    membership_cards_history=36989120,
    payment_cards=8088000,
    payment_cards_history=8088000,
    transactions=369891200,
)


barclays_2021 = DataConfig(
    name="barclays_2021",
    membership_plans=13,
    users=1094000,
    users_history=2188000,
    membership_cards=7504840,
    membership_cards_history=29975600,
    payment_cards=1641000,
    payment_cards_history=2461500,
    transactions=24615000,
)


barclays_2022_old = DataConfig(
    name="barclays_2022",
    membership_plans=26,
    users=8192000,
    users_history=8192000,
    membership_cards=56197120,
    membership_cards_history=56197120,
    payment_cards=12288000,
    payment_cards_history=12288000,
    transactions=561971200,
)


barclays_2022 = DataConfig(
    name="barclays_2022",
    membership_plans=36,
    users=6269000,
    users_history=12538000,
    membership_cards=43005340,
    membership_cards_history=171770600,
    payment_cards=9403500,
    payment_cards_history=14105250,
    transactions=141052500,
)


barclays_2023_old = DataConfig(
    name="barclays_2023",
    membership_plans=35,
    users=11011000,
    users_history=11011000,
    membership_cards=75535460,
    membership_cards_history=75535460,
    payment_cards=16516500,
    payment_cards_history=16516500,
    transactions=755354600,
)


barclays_2023 = DataConfig(
    name="barclays_2023",
    membership_plans=74,
    users=14615000,
    users_history=29230000,
    membership_cards=100258900,
    membership_cards_history=400451000,
    payment_cards=21922500,
    payment_cards_history=32883750,
    transactions=328837500,
)


barclays_2024_old = DataConfig(
    name="barclays_2024",
    membership_plans=50,
    users=13593000,
    users_history=13593000,
    membership_cards=93247980,
    membership_cards_history=93247980,
    payment_cards=20389500,
    payment_cards_history=20389500,
    transactions=932479800,
)


barclays_2024 = DataConfig(
    name="barclays_2024",
    membership_plans=104,
    users=25773000,
    users_history=51546000,
    membership_cards=176802780,
    membership_cards_history=706180200,
    payment_cards=38659500,
    payment_cards_history=57989250,
    transactions=579892500,
)


barclays_internal_test = DataConfig(
    name="barclays_internal_test",
    membership_plans=3,
    users=5000,
    users_history=5000,
    membership_cards=5000,
    membership_cards_history=5000,
    payment_cards=2000,
    payment_cards_history=2000,
    transactions=10000,
)

all_configs = [
    test,
    benchmark,
    barclays_2021,
    barclays_2022,
    barclays_2023,
    barclays_2024,
    barclays_internal_test,
    benchmark_old,
    barclays_2021_old,
    barclays_2022_old,
    barclays_2023_old,
    barclays_2024_old,
]
all_config_names = [config.name for config in all_configs]
