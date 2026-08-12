"""
Purpose: 
Orchestrates the entire AryaCrypt encryption and decryption lifecycle.

Documentation: 
Ties together the custom AryaCrypt framework (for key material generation) 
with standard PBKDF2 (for key derivation) and AES-256-GCM (for encryption).
It packs the resulting ciphertext and metadata (Salt, Nonce, Tag) into a 
single transportable binary payload.

Unit Test Suggestions:
- Ensure encrypt_data returns a byte array larger than the plaintext.
- Ensure decrypt_data(seed, encrypt_data(seed, text)) == text.
- Ensure decrypt_data with a different seed raises an exception.
"""

from app.aryacrypt.service import AryaCryptService
from app.encryption.key_manager import KeyManager
from app.encryption.aes_gcm import AESGCMCipher
from app.encryption.metadata import PayloadMetadata

class EncryptionService:
    def __init__(self):
        self.aryacrypt = AryaCryptService()

    def encrypt_data(self, numeric_seed: int, plaintext: bytes) -> bytes:
        """
        Encrypts the plaintext using the AryaCrypt framework keying logic.
        
        Args:
            numeric_seed (int): The user's secret numeric pin/seed.
            plaintext (bytes): The raw file data to encrypt.
            
        Returns:
            bytes: The packed payload containing [Salt][Nonce][Tag][Ciphertext].
        """
        # 1. Generate phonetic pre-image from the AryaCrypt framework
        phonetic_password = self.aryacrypt.generate_preprocessing_stream(numeric_seed)
        
        # 2. Generate random salt and derive the 256-bit AES key
        salt = KeyManager.generate_salt()
        key = KeyManager.derive_key(phonetic_password, salt)
        
        # 3. Encrypt the data
        nonce, ciphertext, tag = AESGCMCipher.encrypt(key, plaintext)
        
        # 4. Pack all metadata securely into the final payload
        return PayloadMetadata.pack(salt, nonce, tag, ciphertext)

    def decrypt_data(self, numeric_seed: int, encrypted_payload: bytes) -> bytes:
        """
        Decrypts a packed payload using the AryaCrypt framework keying logic.
        
        Args:
            numeric_seed (int): The user's secret numeric pin/seed.
            encrypted_payload (bytes): The packed data.
            
        Returns:
            bytes: The original plaintext.
            
        Raises:
            ValueError: If the payload is too small.
            cryptography.exceptions.InvalidTag: If data is tampered or the seed is wrong.
        """
        # 1. Unpack the metadata from the payload
        salt, nonce, tag, ciphertext = PayloadMetadata.unpack(encrypted_payload)
        
        # 2. Re-generate the phonetic pre-image using the seed
        phonetic_password = self.aryacrypt.generate_preprocessing_stream(numeric_seed)
        
        # 3. Re-derive the AES key using the extracted salt
        key = KeyManager.derive_key(phonetic_password, salt)
        
        # 4. Authenticate and decrypt
        return AESGCMCipher.decrypt(key, nonce, tag, ciphertext)
