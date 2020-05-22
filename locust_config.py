
TEST_SUITE = {
    "get_service": True,
    "get_membership_plans": True,
    "get_membership_plan_id": True,
    "post_membership_cards_single_property_join": True,
    "patch_membership_cards_id_ghost": True,
    "post_payment_cards_single_property": True,
    "post_membership_cards_single_property_add": True,
    "post_payment_cards_multiple_property": True,
    "get_membership_card_single_property": True,
    "patch_membership_card_id_payment_card_id_single_property": False,  # Barclays don't use this endpoint
    "patch_payment_card_id_membership_card_id_single_property": False,  # Barclays don't use this endpoint
    "post_membership_cards_multiple_property": True,
    "patch_membership_card_id_payment_card_id_multiple_property": False,  # Barclays don't use this endpoint
    "patch_payment_card_id_membership_card_id_multiple_property": False,  # Barclays don't use this endpoint
    "get_membership_card_multiple_property": True,
    "patch_membership_cards_id_add": True,
    "get_payment_cards": True,
    "get_membership_cards": True,
    "delete_payment_card_multiple_property": True,
    "delete_payment_card_single_property": True,
    "delete_membership_card": True,
    "delete_service": True,
    "stop_locust_after_test_suite": True,
}


def check_suite_whitelist(test_func):
    if TEST_SUITE.get(test_func.__name__):
        return test_func
    else:
        return lambda *args, **kwargs: None
