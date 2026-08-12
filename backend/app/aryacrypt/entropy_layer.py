"""
Purpose:
Analyzes the complexity and mathematical entropy of the generated phonetic strings.

Documentation:
Before passing the generated Aryabhata string to the standard PBKDF2 function,
this layer calculates basic heuristics (length, character variety) to ensure the 
diffusion step actually succeeded in generating a complex pre-image.

Unit Test Suggestions:
- Provide a short string like "ka" (should return low entropy score).
- Provide a massive, varied string (should return high entropy score).
- Test validation threshold mechanisms.
"""

import math
from collections import Counter

class EntropyLayer:
    @staticmethod
    def calculate_shannon_entropy(stream: str) -> float:
        """
        Calculates the Shannon Entropy of the generated phonetic string.
        
        Args:
            stream (str): The Aryabhata phonetic stream.
            
        Returns:
            float: The entropy score in bits per character.
        """
        if not stream:
            return 0.0
            
        length = len(stream)
        frequencies = Counter(stream)
        
        entropy = 0.0
        for count in frequencies.values():
            probability = count / length
            entropy -= probability * math.log2(probability)
            
        return entropy

    @staticmethod
    def validate_minimum_entropy(stream: str, min_threshold: float = 3.0) -> bool:
        """
        Validates that the stream possesses sufficient entropy before hashing.
        
        Args:
            stream (str): The stream to validate.
            min_threshold (float): Minimum acceptable Shannon entropy.
            
        Returns:
            bool: True if entropy is sufficient, False otherwise.
        """
        entropy = EntropyLayer.calculate_shannon_entropy(stream)
        return entropy >= min_threshold
