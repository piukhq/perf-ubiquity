import requests

from data_population.fixtures.client import ALL_CLIENTS, JWT_SECRET, ENCRYPTION_TEST_KEYS
from settings import VAULT_TOKEN, VAULT_URL, CHANNEL_VAULT_PATH


def setup_vault():
    if ENCRYPTION_TEST_KEYS['private_key'] == "replace me with private key":
        raise ValueError("Please replace 'ENCRYPTION_TEST_KEYS' with test private and public keys")

    headers = {"X-Vault-Token": VAULT_TOKEN}
    vault_channels = requests.get(f"{VAULT_URL}/v1/secret{CHANNEL_VAULT_PATH}", headers=headers).json()['data']

    performance_channels = {}
    for client_fixture in ALL_CLIENTS:
        performance_channels[client_fixture["bundle_id"]] = {
            "jwt_secret": JWT_SECRET,
            **ENCRYPTION_TEST_KEYS
        }

    if not all(item in vault_channels.items() for item in performance_channels.items()):
        vault_channels.update(performance_channels)
        requests.post(f"{VAULT_URL}/v1/secret{CHANNEL_VAULT_PATH}", headers=headers, json=vault_channels)

    for client in ALL_CLIENTS:
        keys_url = f"{VAULT_URL}/v1/secret/data/{client['bundle_id']}"
        resp = requests.get(keys_url, headers=headers)
        if resp.status_code == 404:
            data = ENCRYPTION_TEST_KEYS
            requests.post(keys_url, headers=headers, json=data)


if __name__ == "__main__":
    setup_vault()
