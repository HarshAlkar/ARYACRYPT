"""
Purpose:
Orchestrates the conversion of a numeric seed into phonetic fragments.

Documentation:
This engine ties together the PositionalEncoder and the RomanSanskritMapper.
For each base-100 chunk:
- It splits the chunk into tens (Avarga) and units (Varga).
- It looks up the respective consonants.
- It attaches the vowel corresponding to the base-100 exponent (power).

Unit Test Suggestions:
- Test an exact match against a known historical Aryabhata number.
- Ensure 0 is handled elegantly.
- Check combinations of Varga and Avarga (e.g., 34 -> 30 (Avarga 'y') + 4 (Varga 'gh')).
"""

from typing import List
from app.aryacrypt.interfaces import IEncodingEngine, IPositionalEncoder, IRomanMapper

class AryabhataEncodingEngine(IEncodingEngine):
    
    def __init__(self, encoder: IPositionalEncoder, mapper: IRomanMapper):
        self.encoder = encoder
        self.mapper = mapper
        
    def generate_phonetic_fragments(self, numeric_seed: int) -> List[str]:
        chunks = self.encoder.extract_positions(numeric_seed)
        fragments = []
        
        for value, power in chunks:
            if value == 0:
                continue
                
            vowel = self.mapper.map_vowel(power)
            fragment = ""
            
            # Case 1: Pure Varga (1-25)
            if value <= 25:
                consonant = self.mapper.map_varga(value)
                if consonant:
                    fragment = f"{consonant}{vowel}"
            # Case 2: Pure Avarga or mixed Varga/Avarga (26-99)
            else:
                tens = (value // 10) * 10
                units = value % 10
                
                # If units exist and are <= 25, it's a compound
                consonant_parts = []
                if units > 0:
                    varga_c = self.mapper.map_varga(units)
                    if varga_c:
                        consonant_parts.append(varga_c)
                        
                avarga_c = self.mapper.map_avarga(tens)
                if avarga_c:
                    consonant_parts.append(avarga_c)
                    
                combined_consonant = "".join(consonant_parts)
                if combined_consonant:
                    fragment = f"{combined_consonant}{vowel}"
                    
            if fragment:
                fragments.append(fragment)
                
        # Reversing to maintain standard high-order to low-order read logic
        return list(reversed(fragments))
