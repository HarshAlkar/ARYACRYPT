"""
Purpose:
Breaks down large numerical seeds into base-100 positional chunks.

Documentation:
In the Aryabhata numbering system, numbers are represented in base-100.
Odd places (1s, 100s, 10000s) are Varga positions.
Even places (10s, 1000s, 100000s) are Avarga positions.
This encoder takes an integer and returns a list of tuples containing
the base-100 value and its exponent power.

Unit Test Suggestions:
- Input 1: should return [(1, 0)]
- Input 100: should return [(0, 0), (1, 1)]
- Input 299792458: should return [(58, 0), (24, 1), (79, 2), (99, 3), (2, 4)]
"""

from typing import List, Tuple
from app.aryacrypt.interfaces import IPositionalEncoder

class PositionalEncoder(IPositionalEncoder):
    
    def extract_positions(self, numeric_seed: int) -> List[Tuple[int, int]]:
        """
        Extracts base-100 chunks from a numeric seed.
        
        Args:
            numeric_seed (int): The positive integer to encode.
            
        Returns:
            List[Tuple[int, int]]: A list of tuples (chunk_value, power) starting from least significant.
        """
        if numeric_seed == 0:
            return [(0, 0)]
            
        chunks = []
        power = 0
        current_value = numeric_seed
        
        while current_value > 0:
            chunk = current_value % 100
            chunks.append((chunk, power))
            current_value = current_value // 100
            power += 1
            
        return chunks
