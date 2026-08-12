import os


class SaltManager:
    """
    Manages the generation and validation of cryptographic salts used primarily 
    for the PBKDF2 key derivation function.
    
    Responsibilities:
    - Interface with the Operating System's Cryptographically Secure 
      Pseudorandom Number Generator (CSPRNG).
    - Enforce NIST recommendations for minimum salt lengths (16 bytes / 128 bits).
    """

    # NIST recommends a minimum of 16 bytes (128 bits) for PBKDF2 salts
    DEFAULT_SALT_LENGTH_BYTES = 16

    @staticmethod
    def generate_salt(length_bytes: int = DEFAULT_SALT_LENGTH_BYTES) -> bytes:
        """
        Generates a secure, random cryptographic salt using os.urandom.
        
        Args:
            length_bytes (int): The required length of the salt in bytes.
            
        Returns:
            bytes: The securely generated salt.
            
        Raises:
            ValueError: If the requested length is below the NIST recommendation.
        """
        if length_bytes < SaltManager.DEFAULT_SALT_LENGTH_BYTES:
            raise ValueError(
                f"Salt length of {length_bytes} bytes is insecure. "
                f"NIST recommends at least {SaltManager.DEFAULT_SALT_LENGTH_BYTES} bytes."
            )
            
        return os.urandom(length_bytes)

    @staticmethod
    def validate_salt(salt: bytes) -> None:
        """
        Validates an existing salt to ensure it meets the minimum security 
        criteria before it is utilized in the cryptographic pipeline.
        
        Args:
            salt (bytes): The salt to validate.
            
        Raises:
            ValueError: If the salt length is insufficient.
            TypeError: If the salt is not of type bytes.
        """
        if not isinstance(salt, bytes):
            raise TypeError(f"Cryptographic salt must be bytes, got {type(salt).__name__}.")
            
        if len(salt) < SaltManager.DEFAULT_SALT_LENGTH_BYTES:
            raise ValueError(
                f"Provided salt is insecurely short ({len(salt)} bytes). "
                f"Minimum required is {SaltManager.DEFAULT_SALT_LENGTH_BYTES} bytes."
            )
