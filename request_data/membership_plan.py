from data_population.create_tsv import MEMBERSHIP_PLANS


def increment_membership_plan_counter(current_plan_counter):
    new_plan = (current_plan_counter % MEMBERSHIP_PLANS) + 1
    return new_plan
