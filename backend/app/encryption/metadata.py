"""
Purpose: 
Defines the binary format for encrypted file payloads.

Documentation: 
Packages the Salt, Nonce, Auth Tag, and Ciphertext together so they can be 
securely saved to disk and retrieved without managing side-channel databases.
Format: [Salt: 16 bytes] [Nonce: 12 bytes] [Auth Tag: 16 bytes] [Ciphertext: N bytes]

Unit Test Suggestions:
- Pack arbitrary bytes and ensure unpack successfully reverses the process.
- Pack with invalid length arrays (e.g. 15 byte salt) and ensure ValueError is raised.
"""

from typing import Tuple

class PayloadMetadata:
    SALT_SIZE = 16
    NONCE_SIZE = 12
    TAG_SIZE = 16
    HEADER_SIZE = SALT_SIZE + NONCE_SIZE + TAG_SIZE

    @staticmethod
    def pack(salt: bytes, nonce: bytes, tag: bytes, ciphertext: bytes) -> bytes:
        if len(salt) != PayloadMetadata.SALT_SIZE:
            raise ValueError("Invalid salt length")
        if len(nonce) != PayloadMetadata.NONCE_SIZE:
            raise ValueError("Invalid nonce length")
        if len(tag) != PayloadMetadata.TAG_SIZE:
            raise ValueError("Invalid tag length")
            
        return salt + nonce + tag + ciphertext

    @staticmethod
    def unpack(payload: bytes) -> Tuple[bytes, bytes, bytes, bytes]:
        if len(payload) < PayloadMetadata.HEADER_SIZE:
            raise ValueError("Payload is too small to contain required cryptographic metadata")
            
        salt = payload[0:16]
        nonce = payload[16:28]
        tag = payload[28:44]
        ciphertext = payload[44:]
        
        return salt, nonce, tag, ciphertext
