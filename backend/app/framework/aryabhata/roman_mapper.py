import unicodedata
from typing import Optional
from .mapping import AryabhataMapping
from .constants import (
    BASE_DIVISOR, 
    VARGA_MAX_VALUE, 
    AVARGA_START_TENS, 
    MAX_NUMERIC_SEED_SIZE_BITS, 
    MIN_PASSWORD_LENGTH
)


class RomanMapper:
    """
    Handles the end-to-end transformation of a user password into a 
    highly obscure Aryabhata Roman Sanskrit representation.
    
    Responsibilities:
    - Normalizes the input password (Unicode NFC).
    - Validates lengths and types.
    - Generates the massive numeric seed from the normalized bytes.
    - Maps the numeric seed using the Base-100 Aryabhata encoding logic.
    """

    def __init__(self, mapping: Optional[AryabhataMapping] = None):
        """
        Initializes the mapper with a configurable AryabhataMapping instance.
        If none is provided, it uses the default configuration.
        """
        self.mapping = mapping or AryabhataMapping()
        
    def _validate_and_normalize(self, password: str) -> str:
        """
        Validates the password type and length, and applies NFC Unicode 
        normalization for consistent byte representations across platforms.
        """
        if not isinstance(password, str):
            raise TypeError(f"Expected password to be a string, got {type(password).__name__}.")
        
        if len(password) < MIN_PASSWORD_LENGTH:
            raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")
            
        return unicodedata.normalize('NFC', password)

    def _string_to_numeric_seed(self, password: str) -> int:
        """
        Converts the normalized string into a large integer.
        Includes safety bounds against extremely large memory-exhausting strings.
        """
        encoded_bytes = password.encode('utf-8')
        numeric_seed = int.from_bytes(encoded_bytes, byteorder='big')
        
        if numeric_seed.bit_length() > MAX_NUMERIC_SEED_SIZE_BITS:
            raise OverflowError(
                f"Generated numeric seed exceeds the safety limit of {MAX_NUMERIC_SEED_SIZE_BITS} bits."
            )
            
        return numeric_seed

    def encode(self, password: str) -> str:
        """
        Transforms the raw user password into the Aryabhata Roman Sanskrit string.
        
        Args:
            password (str): The raw user input.
            
        Returns:
            str: The Roman Sanskrit representation.
            
        Raises:
            ValueError, TypeError, OverflowError for bad inputs.
            RuntimeError for internal mapping resolution failures.
        """
        normalized_pwd = self._validate_and_normalize(password)
        numeric_seed = self._string_to_numeric_seed(normalized_pwd)
        
        encoded_string = ""
        power = 0
        vowel_count = len(self.mapping.vowel_multipliers)
        
        while numeric_seed > 0:
            remainder = numeric_seed % BASE_DIVISOR
            numeric_seed = numeric_seed // BASE_DIVISOR
            
            # The vowel symbol cycles through the available multipliers based on power
            vowel = self.mapping.get_vowel_symbol(power % vowel_count)
            if not vowel:
                raise RuntimeError(f"Internal Mapping Error: No vowel multiplier found for power index {power % vowel_count}.")
                
            if 0 < remainder <= VARGA_MAX_VALUE:
                # Direct Varga mapping
                consonant = self.mapping.get_varga_symbol(remainder)
                if not consonant:
                    raise RuntimeError(f"Internal Mapping Error: Missing Varga symbol for {remainder}.")
                encoded_string = consonant + vowel + encoded_string
                
            elif remainder > VARGA_MAX_VALUE:
                # Avarga logic for numbers > 25
                tens = (remainder // 10) * 10
                units = remainder % 10
                
                # Append Avarga consonant for tens
                if tens >= AVARGA_START_TENS:
                    avarga_consonant = self.mapping.get_avarga_symbol(tens)
                    if not avarga_consonant:
                        raise RuntimeError(f"Internal Mapping Error: Missing Avarga symbol for {tens}.")
                    encoded_string = avarga_consonant + vowel + encoded_string
                        
                # Append Varga consonant for units, if any
                if units > 0:
                    varga_consonant = self.mapping.get_varga_symbol(units)
                    if not varga_consonant:
                        raise RuntimeError(f"Internal Mapping Error: Missing Varga symbol for {units}.")
                    encoded_string = varga_consonant + vowel + encoded_string
            
            power += 1
            
        return encoded_string
