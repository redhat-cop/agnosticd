import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def encrypt(value, password):

    kdf = PBKDF2HMAC(
      algorithm=hashes.SHA256(),
      length=32,
      salt = b'\x8f\xc6\x9f\x89\x974\xaf+\xfd\x0f\x98\x0e\xecF\xc8\xb1',
      iterations=390000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    f = Fernet(key)
    return f.encrypt(value.encode()).decode()

def decrypt(value, password):
    kdf = PBKDF2HMAC(
      algorithm=hashes.SHA256(),
      length=32,
      salt = b'\x8f\xc6\x9f\x89\x974\xaf+\xfd\x0f\x98\x0e\xecF\xc8\xb1',
      iterations=390000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    f = Fernet(key)
    return f.decrypt(value.encode()).decode()

class FilterModule(object):
    def filters(self):
        return {
            'encrypt': encrypt,
            'decrypt': decrypt
        }

