import json
import os
from pathlib import Path

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError, ServiceRequestError
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from loguru import logger

from ubiquity_performance_test.settings import LOCAL_SECRETS, LOCAL_SECRETS_PATH, SECRETS_LOCATION, VAULT_CONFIG


class KeyVaultError(Exception):
    pass


class KeyVault:
    def __init__(self, vault_url: str) -> None:
        kv_credential = DefaultAzureCredential(
            exclude_environment_credential=True,
            exclude_shared_token_cache_credential=True,
            exclude_visual_studio_code_credential=True,
            exclude_interactive_browser_credential=True,
            additionally_allowed_tenants=["a6e2367a-92ea-4e5a-b565-723830bcc095"],
        )
        self.client = SecretClient(vault_url=vault_url, credential=kv_credential)

    def get_secret(self, secret_name: str) -> str:
        try:
            secret_value = self.client.get_secret(secret_name).value
        except (ServiceRequestError, ResourceNotFoundError, HttpResponseError) as ex:
            raise KeyVaultError(f"Could not retrieve secret {secret_name} due to {ex!r}") from ex
        except AttributeError:
            raise KeyVaultError("Vault not initialised") from None

        if not secret_value:
            raise ValueError(f"Vault returned None value for key '{secret_name}'.")

        return secret_value


class SecretsLoader:
    def __init__(self) -> None:
        self._key_vault = None if LOCAL_SECRETS else KeyVault(vault_url=VAULT_CONFIG["VAULT_URL"])
        self._channel_info: dict | None = None
        self._aes_key: bytes | None = None

    def trigger_loading(self, channel_info: bool = False, aes_key: bool = False) -> None:
        if channel_info:
            self._channel_info = self._get_channel_info()

        if aes_key:
            self._aes_key = self._get_aes_key()

    def _get_channel_info(self) -> dict:
        info: dict = {}

        if LOCAL_SECRETS:
            secrets: dict[str, dict] = json.load(Path(LOCAL_SECRETS_PATH).read_text())  # type: ignore [arg-type]
            info = secrets["channel_secrets"]

        else:
            all_secrets_in_vault = self.key_vault.client.list_properties_of_secrets()

            secrets_to_load: list[str] = []
            for secret in all_secrets_in_vault:
                if secret.name and "ubiquity-channel" in secret.name:
                    secrets_to_load.append(secret.name)
                    logger.info(f"Found channel information: {secret.name} - adding to load list")

            channel_secrets: dict = {}
            for secret_name in secrets_to_load:
                channel_secrets |= json.loads(self.key_vault.get_secret(secret_name))

            api2_private_keys = self.key_vault.get_secret(VAULT_CONFIG["API2_PRIVATE_KEYS_NAME"])

            info |= {"channel_secrets": channel_secrets, "api2_private_keys": json.loads(api2_private_keys)}

        return info

    def _get_aes_key(self) -> bytes:
        raw_value: dict[str, str]

        if SECRETS_LOCATION:
            file_path = os.path.join(SECRETS_LOCATION, "aes-keys")
            raw_value = json.loads(Path(file_path).read_text())

        else:
            raw_value = json.loads(self.key_vault.get_secret("aes-keys"))

        return raw_value["AES_KEY"].encode()

    @property
    def key_vault(self) -> KeyVault:
        if not self._key_vault:
            raise ValueError("KeyVault SecretClient not initialised.")

        return self._key_vault

    @property
    def channel_info(self) -> dict:
        if not self._channel_info:
            self._channel_info = self._get_channel_info()

        return self._channel_info

    @property
    def aes_key(self) -> bytes:
        if not self._aes_key:
            self._aes_key = self._get_aes_key()

        return self._aes_key


vault_secrets = SecretsLoader()
