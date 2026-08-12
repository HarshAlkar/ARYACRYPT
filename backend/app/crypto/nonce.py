import os
import base64


class NonceManager:
    """
    Manages the generation, validation, and serialization of cryptographic 
    nonces (Initialization Vectors) for AES-256-GCM.
    
    Responsibilities:
    - Interface with the OS CSPRNG for cryptographically secure randomness.
    - Strictly enforce the NIST SP 800-38D standard of 12-byte (96-bit) nonces.
    - Provide Base64 encoding/decoding for safe JSON or Database storage.
    """

    # NIST strongly recommends exactly 12 bytes (96 bits) for AES-GCM
    GCM_NONCE_LENGTH_BYTES = 12

    @staticmethod
    def generate(length_bytes: int = GCM_NONCE_LENGTH_BYTES) -> bytes:
        """
        Generates a secure, random cryptographic initialization vector.
        
        Args:
            length_bytes (int): Length of the nonce in bytes.
            
        Returns:
            bytes: The securely generated raw nonce.
            
        Raises:
            ValueError: If the requested length is not exactly 12 bytes.
        """
        if length_bytes != NonceManager.GCM_NONCE_LENGTH_BYTES:
            raise ValueError(
                f"AES-GCM securely requires exactly {NonceManager.GCM_NONCE_LENGTH_BYTES} "
                f"bytes for the nonce to prevent vulnerability. Got {length_bytes} bytes."
            )
            
        return os.urandom(length_bytes)

    @staticmethod
    def validate(nonce: bytes) -> None:
        """
        Validates a raw nonce extracted from storage or incoming payloads.
        
        Args:
            nonce (bytes): The raw nonce to validate.
            
        Raises:
            TypeError: If the nonce is not of type bytes.
            ValueError: If the nonce length deviates from the GCM standard.
        """
        if not isinstance(nonce, bytes):
            raise TypeError(f"Cryptographic nonce must be bytes, got {type(nonce).__name__}.")
            
        if len(nonce) != NonceManager.GCM_NONCE_LENGTH_BYTES:
            raise ValueError(
                f"Invalid nonce length: {len(nonce)} bytes. "
                f"AES-GCM expects exactly {NonceManager.GCM_NONCE_LENGTH_BYTES} bytes."
            )

    @staticmethod
    def encode_base64(nonce: bytes) -> str:
        """
        Serializes the raw byte nonce into a Base64 string for safe text storage.
        
        Args:
            nonce (bytes): The raw cryptographic nonce.
            
        Returns:
            str: The Base64 encoded string.
        """
        NonceManager.validate(nonce)
        return base64.b64encode(nonce).decode('utf-8')

    @staticmethod
    def decode_base64(encoded_nonce: str) -> bytes:
        """
        Deserializes a Base64 string back into the raw cryptographic nonce.
        
        Args:
            encoded_nonce (str): The Base64 string.
            
        Returns:
            bytes: The original raw byte array.
            
        Raises:
            ValueError: If the string is invalid Base64 or the decoded bytes 
                        do not match AES-GCM length requirements.
        """
        if not isinstance(encoded_nonce, str):
            raise TypeError("Encoded nonce must be provided as a string.")
            
        try:
            nonce_bytes = base64.b64decode(encoded_nonce)
        except Exception as e:
            raise ValueError(f"Failed to decode Base64 nonce. Invalid format: {e}") from e
            
        NonceManager.validate(nonce_bytes)
        return nonce_bytes
