from typing import Optional
from .mapping import AryabhataMapping
from .positional import PositionalCalculator


class AryabhataDecoder:
    """
    Reverses the Aryabhata Framework encoding process.
    
    Responsibilities:
    - Parses and tokenizes the Roman Sanskrit Phonetic String.
    - Applies inverse positional mathematics to reconstruct the Numeric Stream.
    - Decodes the massive integer (Numeric Stream) back into the Original Password.
    """
    
    def __init__(self, mapping: Optional[AryabhataMapping] = None):
        self.mapping = mapping or AryabhataMapping()
        self.positional = PositionalCalculator()

    def numeric_to_password(self, numeric_seed: int) -> str:
        """
        Converts a deterministic massive integer (Numeric Stream) directly 
        back into the original UTF-8 string password.
        
        Args:
            numeric_seed (int): The massive integer to decode.
            
        Returns:
            str: The original user password.
            
        Raises:
            ValueError: If the byte stream cannot be decoded as valid UTF-8.
        """
        if numeric_seed == 0:
            return ""
            
        byte_length = (numeric_seed.bit_length() + 7) // 8
        if byte_length == 0:
            return ""
            
        try:
            password_bytes = numeric_seed.to_bytes(byte_length, byteorder='big')
            return password_bytes.decode('utf-8')
        except UnicodeDecodeError as e:
            raise ValueError(
                f"Failed to decode numeric stream to UTF-8. The data might be "
                f"corrupted or it was not generated from a valid string seed: {e}"
            )

    def roman_to_numeric(self, phonetic_string: str) -> int:
        """
        Parses the Aryabhata phonetic string from right to left, identifying 
        syllables based on expected positional vowels, and reconstructs 
        the large numeric stream using Base-100 rules.
        
        Args:
            phonetic_string (str): The Aryabhata Roman string.
            
        Returns:
            int: The reconstructed massive integer (Numeric Stream).
            
        Raises:
            RuntimeError: On internal mapping resolution errors.
            ValueError: If the string is malformed or exceeds safety depth limits.
        """
        if not phonetic_string:
            return 0
            
        total_value = 0
        current_str = phonetic_string
        power = 0
        vowel_count = len(self.mapping.vowel_multipliers)
        
        # Sort symbols by length descending to ensure greedy matching 
        # (e.g., matching 'kh' before 'k', or 'ai' before 'i')
        sorted_vowels = sorted(self.mapping.vowel_multipliers, key=len, reverse=True)
        
        # We must map symbols to their values based on the internal dictionaries
        varga_items = sorted(self.mapping._sym_to_varga_val.items(), key=lambda x: len(x[0]), reverse=True)
        avarga_items = sorted(self.mapping._sym_to_avarga_val.items(), key=lambda x: len(x[0]), reverse=True)
        
        while current_str:
            if power > 10000:
                raise ValueError("Exceeded maximum parsing depth. Malformed or unsafely large Aryabhata string.")
                
            expected_vowel = self.mapping.get_vowel_symbol(power % vowel_count)
            if not expected_vowel:
                raise RuntimeError(f"Internal Mapping Error: No vowel for power index {power % vowel_count}")
                
            # Check if the current trailing syllable belongs to this specific power
            if current_str.endswith(expected_vowel):
                current_str = current_str[:-len(expected_vowel)]
                cluster_val = 0
                
                # 1. Greedily extract Varga (Units)
                for varga_sym, varga_val in varga_items:
                    if current_str.endswith(varga_sym):
                        cluster_val += varga_val
                        current_str = current_str[:-len(varga_sym)]
                        break
                        
                # 2. Greedily extract Avarga (Tens)
                for avarga_sym, avarga_val in avarga_items:
                    if current_str.endswith(avarga_sym):
                        cluster_val += avarga_val
                        current_str = current_str[:-len(avarga_sym)]
                        break
                        
                # Apply the power multiplier to the extracted base value
                total_value += self.positional.apply_positional_weight(cluster_val, power)
                
            # Increment power regardless, because zero values (remainders of 0) 
            # do not output a syllable in the Aryabhata algorithm.
            power += 1
            
        return total_value

    def decode(self, phonetic_string: str) -> str:
        """
        Full end-to-end reversal of the Aryabhata Framework process:
        Roman Phonetic String -> Numeric Stream -> Original Password
        
        Args:
            phonetic_string (str): The encoded Roman Sanskrit string.
            
        Returns:
            str: The original user password.
        """
        numeric_seed = self.roman_to_numeric(phonetic_string)
        return self.numeric_to_password(numeric_seed)
