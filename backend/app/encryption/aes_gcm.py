"""
Purpose: 
Standard, unmodified AES-256-GCM implementation.

Documentation: 
Encrypts and decrypts byte streams utilizing the derived key.
GCM inherently provides authenticated encryption, meaning any tampering 
with the ciphertext will raise an InvalidTag exception upon decryption.

Unit Test Suggestions:
- Encrypt a known string, then decrypt it and verify they match.
- Tamper with a single byte of the ciphertext and ensure an exception is raised upon decryption.
"""

import os
from typing import Tuple
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class AESGCMCipher:
    NONCE_SIZE = 12

    @staticmethod
    def generate_nonce() -> bytes:
        """Generates a secure 12-byte initialization vector (nonce)."""
        return os.urandom(AESGCMCipher.NONCE_SIZE)

    @staticmethod
    def encrypt(key: bytes, plaintext: bytes) -> Tuple[bytes, bytes, bytes]:
        """
        Encrypts the plaintext using AES-256-GCM.
        
        Args:
            key (bytes): The 32-byte AES key.
            plaintext (bytes): The data to encrypt.
            
        Returns:
            Tuple[bytes, bytes, bytes]: (nonce, ciphertext, tag)
        """
        nonce = AESGCMCipher.generate_nonce()
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        return nonce, ciphertext, encryptor.tag

    @staticmethod
    def decrypt(key: bytes, nonce: bytes, tag: bytes, ciphertext: bytes) -> bytes:
        """
        Decrypts the ciphertext using AES-256-GCM and verifies authenticity.
        
        Args:
            key (bytes): The 32-byte AES key.
            nonce (bytes): The 12-byte initialization vector.
            tag (bytes): The 16-byte authentication tag.
            ciphertext (bytes): The encrypted payload.
            
        Returns:
            bytes: The original plaintext.
            
        Raises:
            cryptography.exceptions.InvalidTag: If the data has been altered.
        """
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return plaintext
