import requests

from data_population.fixtures.client import ALL_CLIENTS
from request_data.membership_plan import ClientBundleIDs
from settings import VAULT_TOKEN, VAULT_URL, CHANNEL_VAULT_PATH


def setup_vault():
    headers = {"X-Vault-Token": VAULT_TOKEN}
    vault_channels = requests.get(f"{VAULT_URL}/v1/secret{CHANNEL_VAULT_PATH}", headers=headers).json()['data']

    test_keys_url = f"{VAULT_URL}/v1/secret/data/{ClientBundleIDs.BARCLAYS}"
    test_payment_card_keys = requests.get(test_keys_url, headers=headers).json()['data']

    all_channels = {}
    for client_fixture in ALL_CLIENTS:
        all_channels[client_fixture["bundle_id"]] = {
            "jwt_secret": "testsecret",
            "private_key": test_payment_card_keys['data']['private_key'],
            "public_key": test_payment_card_keys['data']['public_key']
        }

    if not all(item in vault_channels.items() for item in all_channels.items()):
        all_channels.update(vault_channels)
        requests.post(f"{VAULT_URL}/v1/secret{CHANNEL_VAULT_PATH}", headers=headers, json=all_channels)

    for client in ALL_CLIENTS:
        keys_url = f"{VAULT_URL}/v1/secret/data/{client['bundle_id']}"
        resp = requests.get(keys_url, headers=headers)
        if resp.status_code == 404:
            data = test_payment_card_keys
            requests.post(keys_url, headers=headers, json=data)


if __name__ == "__main__":
    setup_vault()
