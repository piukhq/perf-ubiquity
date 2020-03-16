PAYMENT_SCHEME_INFO = {
    "amex": {
        "pk": 1,
        "name": "American Express",
        "url": "https://www.americanexpress.com",
        "input_label": "12345566788",
        "system": "amex",
        "token_method": 0,
        "image": "schemes/Amex-Payment.png",
    },
    "mastercard": {
        "pk": 2,
        "name": "Mastercard",
        "url": "http://www.mastercard.co.uk/",
        "input_label": "Long Card Number",
        "system": "mastercard",
        "token_method": 0,
        "image": "schemes/Mastercard-Payment_1goHQYv.png",
    },
    "visa": {
        "pk": 3,
        "name": "Visa",
        "url": "http://www.visa.com",
        "input_label": "Long Card Number",
        "system": "visa",
        "token_method": 2,
        "image": "schemes/Visa-Payment_DWQzhta.png",
    },
}

ALL_PAYMENT_PROVIDER_STATUS_MAPPINGS = [
    [9, "test", 3, 3],
    [10, "BINK_UNKNOWN", 6, 3],
    [12, "BINK_UNKNOWN", 6, 2],
    [11, "duplicate test", 2, 2],
    [15, "SERVER DOWN TEST", 5, 2],
    [18, "not a provider test", 3, 2],
    [19, "not a provider test", 3, 1],
    [20, "BINK_UNKNOWN", 6, 1],
    [21, "not a provider test 2", 3, 1],
    [2, "record_count_mismatch", 5, 1],
]
