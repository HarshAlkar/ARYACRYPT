"""
Purpose:
Maps numerical values to Roman-Sanskrit equivalents based on Aryabhata's tables.

Documentation:
According to Aryabhata:
- Varga letters (ka to ma) map to 1-25.
- Avarga letters (ya to ha) map to 30, 40, 50, 60, 70, 80, 90, 100.
- Vowels denote positional base-100 powers: 
  0 -> a, 1 -> i, 2 -> u, 3 -> ri, 4 -> lri, 5 -> e, 6 -> ai, 7 -> o, 8 -> au.

Unit Test Suggestions:
- map_varga(1) -> 'k'
- map_varga(25) -> 'm'
- map_avarga(30) -> 'y'
- map_vowel(0) -> 'a'
- map_vowel(1) -> 'i'
"""

from app.aryacrypt.interfaces import IRomanMapper

class RomanSanskritMapper(IRomanMapper):
    
    # 1 to 25
    VARGA_MAP = {
        1: 'k', 2: 'kh', 3: 'g', 4: 'gh', 5: 'ng',
        6: 'c', 7: 'ch', 8: 'j', 9: 'jh', 10: 'ny',
        11: 't', 12: 'th', 13: 'd', 14: 'dh', 15: 'n',
        16: 't', 17: 'th', 18: 'd', 19: 'dh', 20: 'n',
        21: 'p', 22: 'ph', 23: 'b', 24: 'bh', 25: 'm'
    }
    
    # 30 to 100 in steps of 10
    AVARGA_MAP = {
        3: 'y',  # representing 30 in the tens place
        4: 'r',  # 40
        5: 'l',  # 50
        6: 'v',  # 60
        7: 's',  # 70 (ś)
        8: 'sh', # 80 (ṣ)
        9: 's',  # 90
        10: 'h'  # 100
    }
    
    # Base-100 powers
    VOWEL_MAP = {
        0: 'a',
        1: 'i',
        2: 'u',
        3: 'ri',
        4: 'lri',
        5: 'e',
        6: 'ai',
        7: 'o',
        8: 'au'
    }
    
    def map_varga(self, value: int) -> str:
        if value < 1 or value > 25:
            return ""
        return self.VARGA_MAP.get(value, "")
        
    def map_avarga(self, value: int) -> str:
        # We expect a tens value (e.g., 30, 40) divided by 10, meaning 3, 4.
        tens_digit = value // 10
        if tens_digit < 3 or tens_digit > 10:
            return ""
        return self.AVARGA_MAP.get(tens_digit, "")
        
    def map_vowel(self, power: int) -> str:
        # Repeating vowels cyclically for extreme large numbers beyond au
        mapped_power = power % len(self.VOWEL_MAP)
        return self.VOWEL_MAP.get(mapped_power, "")
