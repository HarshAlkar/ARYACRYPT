from typing import List, Optional, Tuple
from .mapping import AryabhataMapping
from .positional import PositionalCalculator
from .constants import VARGA_MAX_VALUE, AVARGA_START_TENS


class AryabhataEncoder:
    """
    Core engine responsible for translating between numeric seeds and 
    their Aryabhata phonetic representations, using configurable mappings
    and strict positional encoding rules.
    
    Responsibilities:
    - Accept Roman Mapping definitions.
    - Apply Positional Encoding mathematics.
    - Generate Aryabhata Numeric Values.
    - Return fully transformed and encoded data strings.
    """

    def __init__(self, mapping: Optional[AryabhataMapping] = None):
        self.mapping = mapping or AryabhataMapping()
        self.positional = PositionalCalculator()

    def encode_numeric_seed(self, numeric_seed: int) -> str:
        """
        Takes a large numeric value, breaks it down positionally (base-100),
        and applies the Roman character mapping to generate the final 
        Aryabhata string.
        
        Args:
            numeric_seed (int): The large integer to encode.
            
        Returns:
            str: The Roman Sanskrit phonetic string.
        """
        # Decompose the number using the positional mathematics module
        components = self.positional.decompose_number(numeric_seed)
        
        encoded_string = ""
        vowel_count = len(self.mapping.vowel_multipliers)
        
        for remainder, power in components:
            # Map the power to its respective vowel
            vowel = self.mapping.get_vowel_symbol(power % vowel_count)
            if not vowel:
                raise RuntimeError(f"Missing vowel mapping for power index {power % vowel_count}")
                
            syllable = ""
            
            # Varga Processing (1 to 25)
            if 0 < remainder <= VARGA_MAX_VALUE:
                syllable = self.mapping.get_varga_symbol(remainder) or ""
                
            # Avarga Processing (> 25)
            elif remainder > VARGA_MAX_VALUE:
                tens = (remainder // 10) * 10
                units = remainder % 10
                
                avarga_part = ""
                varga_part = ""
                
                if tens >= AVARGA_START_TENS:
                    avarga_part = self.mapping.get_avarga_symbol(tens) or ""
                    
                if units > 0:
                    varga_part = self.mapping.get_varga_symbol(units) or ""
                    
                # Combine parts: Avarga consonant followed by Varga consonant
                syllable = avarga_part + varga_part
            
            if syllable:
                # Prepend because higher powers are extracted later
                # but in reading order, smaller powers often appear first or last
                # depending on exact Sanskrit grammar. We prepend to maintain endianness.
                encoded_string = syllable + vowel + encoded_string
                
        return encoded_string

    def _decode_syllable(self, consonant_cluster: str, vowel: str, power: int) -> int:
        """
        Converts a single phonetic syllable back into its numeric value.
        (Internal utility to fulfill the 'Generate Aryabhata Numeric Values' requirement)
        """
        base_value = 0
        
        # This is a simplified decoding logic representing the reverse mapping
        # Because of historical ambiguities (e.g. 'r', 'l' as both vowels and consonants),
        # a full tokenizer is required for robust production decoding.
        
        # Extract direct Varga match
        varga_val = self.mapping.get_varga_value(consonant_cluster)
        if varga_val:
            base_value += varga_val
            
        # Extract direct Avarga match
        avarga_val = self.mapping.get_avarga_value(consonant_cluster)
        if avarga_val:
            base_value += avarga_val
            
        return self.positional.apply_positional_weight(base_value, power)

    def generate_numeric_values(self, mapped_symbols: List[Tuple[str, str, int]]) -> int:
        """
        Accepts pre-parsed Roman mapping symbols and applies positional 
        encoding to generate the final Aryabhata numeric values.
        
        Args:
            mapped_symbols: A list of tuples containing (consonant_cluster, vowel, power)
            
        Returns:
            int: The reconstructed large numeric integer.
        """
        total_value = 0
        for consonant, vowel, power in mapped_symbols:
            total_value += self._decode_syllable(consonant, vowel, power)
            
        return total_value
