import os
import base64


class SaltManager:
    """
    Manages the complete lifecycle of cryptographic salts.
    
    Responsibilities:
    - Securely generate salts via OS-level CSPRNGs.
    - Validate salts against NIST minimum length requirements.
    - Encode and serialize salts into safe string formats (e.g., Base64) 
      for database storage or network transmission.
    """

    # NIST SP 800-132 recommends a minimum of 128 bits (16 bytes)
    MIN_SALT_LENGTH_BYTES = 16

    @staticmethod
    def generate(length_bytes: int = MIN_SALT_LENGTH_BYTES) -> bytes:
        """
        Generates a secure, random cryptographic salt.
        
        Args:
            length_bytes (int): Length of the salt in bytes.
            
        Returns:
            bytes: The securely generated raw bytes.
            
        Raises:
            ValueError: If the requested length is below security standards.
        """
        if length_bytes < SaltManager.MIN_SALT_LENGTH_BYTES:
            raise ValueError(
                f"Salt length of {length_bytes} bytes is insecure. "
                f"NIST recommends a minimum of {SaltManager.MIN_SALT_LENGTH_BYTES} bytes."
            )
            
        return os.urandom(length_bytes)

    @staticmethod
    def validate(salt: bytes) -> None:
        """
        Validates an existing raw salt to ensure it is secure enough for 
        key derivation functions like PBKDF2.
        
        Args:
            salt (bytes): The raw salt to validate.
            
        Raises:
            TypeError: If the salt is not of type bytes.
            ValueError: If the salt is insufficiently long.
        """
        if not isinstance(salt, bytes):
            raise TypeError(f"Cryptographic salt must be bytes, got {type(salt).__name__}.")
            
        if len(salt) < SaltManager.MIN_SALT_LENGTH_BYTES:
            raise ValueError(
                f"Provided salt is insecurely short ({len(salt)} bytes). "
                f"Minimum required is {SaltManager.MIN_SALT_LENGTH_BYTES} bytes."
            )

    @staticmethod
    def encode_base64(salt: bytes) -> str:
        """
        Serializes the raw byte salt into a Base64 encoded string.
        Useful when storing the salt alongside metadata in a text format or JSON.
        
        Args:
            salt (bytes): The raw cryptographic salt.
            
        Returns:
            str: The Base64 encoded string representation.
        """
        # Ensure we never serialize an invalid salt
        SaltManager.validate(salt)
        return base64.b64encode(salt).decode('utf-8')

    @staticmethod
    def decode_base64(encoded_salt: str) -> bytes:
        """
        Deserializes a Base64 string back into the raw cryptographic salt bytes.
        
        Args:
            encoded_salt (str): The Base64 string.
            
        Returns:
            bytes: The original raw byte array.
            
        Raises:
            ValueError: If the string is not valid Base64 or the resulting 
                        salt violates security validation rules.
        """
        if not isinstance(encoded_salt, str):
            raise TypeError("Encoded salt must be provided as a string.")
            
        try:
            salt_bytes = base64.b64decode(encoded_salt)
        except Exception as e:
            raise ValueError(f"Failed to decode Base64 salt. Invalid format: {e}") from e
            
        SaltManager.validate(salt_bytes)
        return salt_bytes
