import base64
import hashlib
import json

from Crypto import Random
from Crypto.Cipher import AES

from ubiquity_performance_test.vault import vault_secrets


class AESCipher:
    def __init__(self, key: bytes) -> None:
        self.bs = 32
        self.key = hashlib.sha256(key).digest()

    def encrypt(self, raw: str) -> bytes:
        if raw == "":
            raise TypeError("Cannot encrypt nothing")

        b_raw = self._pad(raw.encode("utf-8"))
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(b_raw))

    def decrypt(self, enc: bytes) -> str:
        if enc == "":
            raise TypeError("Cannot decrypt nothing")
        enc = base64.b64decode(enc)
        iv = enc[: AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size :])).decode("utf-8")

    def _pad(self, s: bytes) -> bytes:
        length = self.bs - (len(s) % self.bs)
        return s + bytes([length]) * length

    @staticmethod
    def _unpad(s: bytes) -> bytes:
        return s[: -ord(s[len(s) - 1 :])]


def decrypt_credentials(credential: str) -> dict:
    aes = AESCipher(vault_secrets.aes_key)
    return json.loads(aes.decrypt(credential.replace(" ", "+").encode("utf-8")))


def encrypt_credentials(credential: str) -> str:
    aes = AESCipher(vault_secrets.aes_key)
    return aes.encrypt(credential).decode("utf-8")
