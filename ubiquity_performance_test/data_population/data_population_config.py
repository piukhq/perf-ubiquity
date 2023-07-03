from dataclasses import dataclass

from ubiquity_performance_test.data_population.fixtures.membership_plan import SCHEME_SLUGS


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
    real_plans: bool = False


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
    membership_plans=13,
    users=273500,
    users_history=547000,
    membership_cards=1876210,
    membership_cards_history=7493900,
    payment_cards=410250,
    payment_cards_history=615375,
    transactions=6153750,
)


benchmark = DataConfig(
    name="benchmark",
    membership_plans=16,
    users=132902,
    users_history=265804,
    membership_cards=911708,
    membership_cards_history=3646831,
    payment_cards=199353,
    payment_cards_history=299030,
    transactions=1993530,
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


barclays_2022 = DataConfig(
    name="barclays_2022",
    membership_plans=16,
    users=531608,
    users_history=1063216,
    membership_cards=3646830,
    membership_cards_history=14587323,
    payment_cards=797412,
    payment_cards_history=1196118,
    transactions=7974120,
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


harmonia_real_slugs = DataConfig(
    name="harmonia_real_slugs",
    membership_plans=len(SCHEME_SLUGS),
    users=5000,
    users_history=5000,
    membership_cards=5000,
    membership_cards_history=5000,
    payment_cards=2000,
    payment_cards_history=2000,
    transactions=10000,
    real_plans=True,
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
    harmonia_real_slugs,
]
all_config_names = [config.name for config in all_configs]
