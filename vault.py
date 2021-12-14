import json

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError, ServiceRequestError
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from settings import LOCAL_SECRETS, LOCAL_SECRETS_PATH, VAULT_CONFIG

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

        channel_info = {}

        if LOCAL_SECRETS:
            with open(LOCAL_SECRETS_PATH) as fp:
                secrets = json.load(fp)
                channel_info = secrets['channel_secrets']
        else:
            vault = KeyVault(vault_url=VAULT_CONFIG["VAULT_URL"])
            channel_secrets = vault.get_secret(VAULT_CONFIG["CHANNEL_SECRET_NAME"])
            api2_private_keys = vault.get_secret(VAULT_CONFIG["API2_PRIVATE_KEYS_NAME"])
            channel_info.update({
                'channel_secrets': json.loads(channel_secrets),
                'api2_private_keys': json.loads(api2_private_keys)
            })

    return channel_info
