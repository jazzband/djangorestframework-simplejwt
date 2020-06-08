import base64
import hashlib
from cryptography.hazmat.primitives import serialization
from jwt.algorithms import RSAAlgorithm


class BaseKeyID:
    def __init__(self, public_key):
        prepared_key = RSAAlgorithm.prepare_key(None, public_key)
        self.public_bytes = prepared_key.public_bytes(encoding=serialization.Encoding.DER,
                                                      format=serialization.PublicFormat.SubjectPublicKeyInfo)

    def __str__(self):
        raise NotImplemented


class PlainKeyID(BaseKeyID):
    def __init__(self, public_key):
        super().__init__(public_key)
        self.hash_bytes = hashlib.sha256(self.public_bytes).digest()

    def __str__(self):
        return self.hash_bytes.hex()


class LibtrustKeyID(BaseKeyID):
    def __init__(self, public_key):
        super().__init__(public_key)
        self.hash_bytes = hashlib.sha256(self.public_bytes).digest()[:30]

    def __str__(self):
        hash_str = base64.b32encode(self.hash_bytes).decode('ascii')
        return ':'.join(hash_str[i:i + 4] for i in range(0, len(hash_str), 4))
