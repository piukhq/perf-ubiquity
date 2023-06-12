import base64
import hashlib
import json
import os

from Crypto import Random
from Crypto.Cipher import AES

import settings


class AESCipher(object):
    def __init__(self, key):
        self.bs = 32
        self.key = hashlib.sha256(key).digest()

    def encrypt(self, raw):
        if raw == "":
            raise TypeError("Cannot encrypt nothing")
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        if enc == "":
            raise TypeError("Cannot decrypt nothing")
        enc = base64.b64decode(enc)
        iv = enc[: AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size :])).decode("utf-8")

    def _pad(self, s):
        length = self.bs - (len(s) % self.bs)
        return s + bytes([length]) * length

    @staticmethod
    def _unpad(s):
        return s[: -ord(s[len(s) - 1 :])]


def get_aes_key(filename: str):
    with open(filename) as reader:
        vault_aes_keys = reader.read()
        aes_key = json.loads(vault_aes_keys)["AES_KEY"]
    return aes_key.encode()


def decrypt_credentials(credentials: str) -> dict:
    aes = AESCipher(get_aes_key(os.path.join(settings.SECRETS_LOCATION, "aes-keys")))
    return json.loads(aes.decrypt(credentials.replace(" ", "+")))


def encrypt_credentials(credentials: dict) -> str:
    aes = AESCipher(get_aes_key(os.path.join(settings.SECRETS_LOCATION, "aes-keys")))
    return aes.encrypt(json.dumps(credentials).encode()).decode("utf-8")
