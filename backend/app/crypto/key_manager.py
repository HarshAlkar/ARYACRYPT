import hashlib


class KeyManager:
    """
    Manages the complete key generation pipeline, acting as the secure bridge 
    between the AryaCrypt Preprocessing Framework and standard cryptographic primitives.
    
    Responsibilities:
    - Receive the preprocessed, heavily obfuscated AryaCrypt Byte Stream.
    - Feed the stream into an unmodified PBKDF2-HMAC-SHA256 algorithm.
    - Generate and return a secure 256-bit symmetric key for AES-256-GCM.
    """

    # NIST Recommended Security Parameters
    HASH_ALGORITHM = 'sha256'
    DEFAULT_ITERATIONS = 600_000
    KEY_LENGTH_BYTES = 32  # 32 bytes = 256 bits

    @staticmethod
    def derive_key(aryacrypt_stream: bytes, salt: bytes, iterations: int = DEFAULT_ITERATIONS) -> bytes:
        """
        Derives a strict 256-bit symmetric key using PBKDF2.
        
        This method ensures the underlying cryptographic standards are 100% 
        unmodified, satisfying compliance requirements while leveraging the 
        entropy of the AryaCrypt preprocessing layer.
        
        Args:
            aryacrypt_stream (bytes): The deterministic byte stream output 
                                      from the AryaCrypt framework.
            salt (bytes): A cryptographically secure random salt (minimum 16 bytes).
            iterations (int): The algorithmic computational cost (iteration count).
            
        Returns:
            bytes: A 32-byte (256-bit) ephemeral symmetric key.
            
        Raises:
            TypeError: If the inputs are not raw byte arrays.
            ValueError: If the salt or iteration count violates security minimums.
        """
        if not isinstance(aryacrypt_stream, bytes):
            raise TypeError(f"AryaCrypt stream must be provided as bytes, got {type(aryacrypt_stream).__name__}.")
            
        if not isinstance(salt, bytes):
            raise TypeError(f"Cryptographic salt must be provided as bytes, got {type(salt).__name__}.")
            
        if len(salt) < 16:
            raise ValueError(f"Insecure salt length: {len(salt)} bytes. NIST requires at least 16 bytes.")
            
        # 100,000 is an absolute minimum floor, though 600,000 is the recommended default
        if iterations < 100_000:
            raise ValueError(f"Insecure iteration count: {iterations}. Requires at least 100,000 for PBKDF2-SHA256.")

        # Standard, mathematically unmodified PBKDF2 integration
        ephemeral_key = hashlib.pbkdf2_hmac(
            hash_name=KeyManager.HASH_ALGORITHM,
            password=aryacrypt_stream,
            salt=salt,
            iterations=iterations,
            dklen=KeyManager.KEY_LENGTH_BYTES
        )
        
        return ephemeral_key
