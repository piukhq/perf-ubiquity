from enum import StrEnum


class HermesTables(StrEnum):
    ORGANISATION = "user_organisation"
    CLIENT_APP = "user_clientapplication"
    CLIENT_APP_BUNDLE = "user_clientapplicationbundle"
    USER = "user"
    CONSENT = "ubiquity_serviceconsent"
    CATEGORY = "scheme_category"
    SCHEME = "scheme_scheme"
    SCHEME_BALANCE_DETAILS = "scheme_schemebalancedetails"
    SCHEME_CONTENT = "scheme_schemecontent"
    QUESTION = "scheme_schemecredentialquestion"
    SCHEME_CONSENT = "scheme_consent"
    THIRD_PARTY_CONSENT_LINK = "scheme_thirdpartyconsentlink"
    SCHEME_IMAGE = "scheme_schemeimage"
    SCHEME_WHITELIST = "scheme_schemebundleassociation"
    VOUCHER_SCHEME = "scheme_voucherscheme"
    MEMBERSHIP_PLAN_DOCUMENTS = "ubiquity_membershipplandocument"
    PAYMENT_CARD_ISSUER = "payment_card_issuer"
    PAYMENT_SCHEME = "payment_card_paymentcard"
    PAYMENT_CARD_IMAGE = "payment_card_paymentcardimage"
    PAYMENT_CARD_ACCOUNT_IMAGE = "payment_card_paymentcardaccountimage"
    PROVIDER_STATUS_MAPPING = "payment_card_providerstatusmapping"
    SCHEME_ACCOUNT = "scheme_schemeaccount"
    PAYMENT_ACCOUNT = "payment_card_paymentcardaccount"
    PAYMENT_ACCOUNT_ENTRY = "ubiquity_paymentcardaccountentry"
    SCHEME_ACCOUNT_ENTRY = "ubiquity_schemeaccountentry"
    ANSWER = "scheme_schemeaccountcredentialanswer"
    PAYMENT_MEMBERSHIP_ENTRY = "ubiquity_paymentcardschemeentry"
    PLL_USER_ASSOCIATION = "ubiquity_plluserassociation"
    VOP_ACTIVATION = "ubiquity_vopactivation"


class HermesHistoryTables(StrEnum):
    HISTORICAL_SCHEME_ACCOUNT = "history_historicalschemeaccount"
    HISTORICAL_PAYMENT_CARD_ACCOUNT = "history_historicalpaymentcardaccount"
    HISTORICAL_PAYMENT_ACCOUNT_ENTRY = "history_historicalpaymentcardaccountentry"
    HISTORICAL_SCHEME_ACCOUNT_ENTRY = "history_historicalschemeaccountentry"
    HISTORICAL_PAYMENT_MEMBERSHIP_ENTRY = "history_historicalpaymentcardschemeentry"
    HISTORICAL_USER = "history_historicalcustomuser"
    HISTORICAL_VOP_ACTIVATION = "history_historicalvopactivation"


class HadesTables(StrEnum):
    TRANSACTIONS = "transaction"
