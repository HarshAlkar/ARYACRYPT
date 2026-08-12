import os


class NonceManager:
    """
    Manages the generation of cryptographic nonces (Initialization Vectors).
    
    Responsibilities:
    - Interface with the Operating System's Cryptographically Secure 
      Pseudorandom Number Generator (CSPRNG).
    - Strictly enforce NIST SP 800-38D recommendations for AES-GCM 
      nonce lengths (96 bits / 12 bytes).
    """

    # NIST strongly recommends exactly 12 bytes (96 bits) for AES-GCM nonces
    GCM_NONCE_LENGTH_BYTES = 12

    @staticmethod
    def generate_nonce(length_bytes: int = GCM_NONCE_LENGTH_BYTES) -> bytes:
        """
        Generates a secure, random cryptographic nonce.
        
        Args:
            length_bytes (int): The required length of the nonce in bytes.
            
        Returns:
            bytes: The securely generated nonce.
            
        Raises:
            ValueError: If the requested length deviates from GCM standards.
        """
        if length_bytes != NonceManager.GCM_NONCE_LENGTH_BYTES:
            raise ValueError(
                f"AES-GCM securely requires exactly {NonceManager.GCM_NONCE_LENGTH_BYTES} "
                f"bytes for the nonce to prevent vulnerability. Got {length_bytes} bytes."
            )
            
        return os.urandom(length_bytes)

    @staticmethod
    def validate_nonce(nonce: bytes) -> None:
        """
        Validates an existing nonce (e.g., extracted during decryption) 
        to ensure it matches AES-GCM structural requirements.
        
        Args:
            nonce (bytes): The initialization vector to validate.
            
        Raises:
            ValueError: If the nonce length is incorrect.
            TypeError: If the nonce is not of type bytes.
        """
        if not isinstance(nonce, bytes):
            raise TypeError(f"Cryptographic nonce must be bytes, got {type(nonce).__name__}.")
            
        if len(nonce) != NonceManager.GCM_NONCE_LENGTH_BYTES:
            raise ValueError(
                f"Invalid nonce length: {len(nonce)} bytes. "
                f"AES-GCM expects exactly {NonceManager.GCM_NONCE_LENGTH_BYTES} bytes."
            )
