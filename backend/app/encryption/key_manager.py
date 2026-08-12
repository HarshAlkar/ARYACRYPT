"""
Purpose: 
Derives secure 256-bit AES keys.

Documentation: 
Uses PBKDF2-HMAC-SHA256. Strictly takes the phonetic string generated 
by the AryaCrypt framework as the keying material. Do NOT modify PBKDF2 
or SHA256 logic.

Unit Test Suggestions:
- Ensure the same phonetic string and salt produce the exact same key.
- Ensure different salts produce entirely different keys for the same string.
"""

import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

class KeyManager:
    ITERATIONS = 600_000  # Modern recommended secure iterations
    KEY_LENGTH = 32       # 256 bits for AES-256

    @staticmethod
    def generate_salt() -> bytes:
        """Generates a secure 16-byte random salt."""
        return os.urandom(16)

    @staticmethod
    def derive_key(phonetic_password: str, salt: bytes) -> bytes:
        """
        Derives an AES-256 key from the AryaCrypt phonetic string and a salt.
        
        Args:
            phonetic_password (str): The AryaCrypt string output.
            salt (bytes): 16 bytes of randomness.
            
        Returns:
            bytes: 32 bytes of secure key material.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=KeyManager.KEY_LENGTH,
            salt=salt,
            iterations=KeyManager.ITERATIONS,
            backend=default_backend()
        )
        return kdf.derive(phonetic_password.encode('utf-8'))
