import json
import logging

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError, ServiceRequestError
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from settings import LOCAL_SECRETS, LOCAL_SECRETS_PATH, VAULT_CONFIG

channel_info = None

logger = logging.getLogger("vault")


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
                channel_info = secrets["channel_secrets"]
        else:
            vault = KeyVault(vault_url=VAULT_CONFIG["VAULT_URL"])

            all_secrets_in_vault = vault.client.list_properties_of_secrets()

            secrets_to_load = []
            for secret in all_secrets_in_vault:
                if "ubiquity-channel" in secret.name:
                    secrets_to_load.append(secret.name)
                    logger.info(f"Found channel information: {secret.name} - adding to load list")

            channel_secrets = {}
            for secret_name in secrets_to_load:
                channel_secrets.update(json.loads(vault.get_secret(secret_name)))

            api2_private_keys = vault.get_secret(VAULT_CONFIG["API2_PRIVATE_KEYS_NAME"])

            channel_info.update({"channel_secrets": channel_secrets, "api2_private_keys": json.loads(api2_private_keys)})

    return channel_info
