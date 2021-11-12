import json

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError, ServiceRequestError
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from settings import CHANNEL_SECRET_NAME, LOCAL_SECRETS, LOCAL_SECRETS_PATH, VAULT_URL

channel_info = None


class KeyVaultError(Exception):
    pass


class KeyVault:
    def __init__(self, vault_url: str) -> None:
        self.client = SecretClient(vault_url=vault_url, credential=DefaultAzureCredential())

    def get_secret(self, secret_name: str) -> str:
        try:
            return self.client.get_secret(secret_name).value
        except (ServiceRequestError, ResourceNotFoundError, HttpResponseError) as ex:
            raise KeyVaultError(f"Could not retrieve secret {secret_name} due to {repr(ex)}") from ex
        except AttributeError:
            raise KeyVaultError("Vault not initialised")


def load_secrets():
    global channel_info
    if channel_info is None:
        if LOCAL_SECRETS:
            with open(LOCAL_SECRETS_PATH) as fp:
                channel_info = json.load(fp)
        else:
            vault = KeyVault(vault_url=VAULT_URL)
            channel_secret = vault.get_secret(CHANNEL_SECRET_NAME)
            channel_info = json.loads(channel_secret)

    return channel_info
