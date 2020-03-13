import requests

from data_population.fixtures import CLIENT_ONE, CLIENT_TWO, CLIENT_RESTRICTED
from request_data.membership_plan import ClientBundleIDs
from settings import VAULT_TOKEN, VAULT_URL, CHANNEL_VAULT_PATH

CLIENT_FIXTURES = [CLIENT_ONE, CLIENT_TWO, CLIENT_RESTRICTED]


def setup_vault():
    headers = {"X-Vault-Token": VAULT_TOKEN}
    vault_channels = requests.get(f"{VAULT_URL}/v1/secret{CHANNEL_VAULT_PATH}", headers=headers).json()['data']
    # barclays_jwt_secret = vault_channels[ClientBundleIDs.BARCLAYS]['jwt_secret']

    all_channels = {}
    for client_fixture in CLIENT_FIXTURES:
        all_channels[client_fixture["bundle_id"]] = {
            "jwt_secret": "testsecret"
        }

    if not all(item in vault_channels.items() for item in all_channels.items()):
        all_channels.update(vault_channels)
        requests.post(f"{VAULT_URL}/v1/secret{CHANNEL_VAULT_PATH}", headers=headers, json=all_channels)

    test_keys_url = f"{VAULT_URL}/v1/secret/data/{ClientBundleIDs.BARCLAYS}"
    test_payment_card_keys = requests.get(test_keys_url, headers=headers).json()['data']

    for client in CLIENT_FIXTURES:
        keys_url = f"{VAULT_URL}/v1/secret/data/{client['bundle_id']}"
        resp = requests.get(keys_url, headers=headers)
        if resp.status_code == 404:
            data = test_payment_card_keys
            requests.post(keys_url, headers=headers, json=data)


if __name__ == "__main__":
    setup_vault()
