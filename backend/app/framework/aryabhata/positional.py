from typing import Tuple
from .constants import BASE_DIVISOR


class PositionalCalculator:
    """
    Handles the positional mathematics of the Aryabhata Number System.
    
    In the Aryabhata system, the positional weight of a number is determined 
    by vowels, which represent sequential powers of 100 (BASE_DIVISOR). 
    This module encapsulates the mathematical transformations to ensure 
    positional logic remains decoupled from the linguistic mapping.
    """

    @staticmethod
    def apply_positional_weight(base_value: int, power: int) -> int:
        """
        Applies the Aryabhata positional weight (power of 100) to a base value.
        
        Args:
            base_value (int): The numeric value of the consonant (e.g., 1 for 'k', 30 for 'y').
            power (int): The power index derived from the vowel (e.g., 0 for 'a', 1 for 'i').
            
        Returns:
            int: The transformed absolute numeric value for this symbol grouping.
            
        Raises:
            ValueError: If the base value or power is negative.
        """
        if base_value < 0 or power < 0:
            raise ValueError("Base value and power must be non-negative integers.")
            
        return base_value * (BASE_DIVISOR ** power)

    @staticmethod
    def calculate_base_and_power(absolute_value: int) -> Tuple[int, int]:
        """
        Decomposes an absolute numeric value into its highest fitting 
        base coefficient and power of 100.
        
        Args:
            absolute_value (int): The large integer to decompose.
            
        Returns:
            Tuple[int, int]: The coefficient (base_value) and the positional power.
        """
        if absolute_value == 0:
            return 0, 0
            
        power = 0
        temp = absolute_value
        while temp >= BASE_DIVISOR:
            temp //= BASE_DIVISOR
            power += 1
            
        return temp, power

    @staticmethod
    def decompose_number(numeric_seed: int) -> list[Tuple[int, int]]:
        """
        Fully decomposes a large numeric seed into a list of (remainder, power) 
        pairs according to the Base-100 logic.
        
        This mimics the core extraction loop of the Aryabhata system.
        
        Args:
            numeric_seed (int): The massive integer to decompose.
            
        Returns:
            list[Tuple[int, int]]: A list of tuples where each is (remainder, power).
        """
        if numeric_seed == 0:
            return [(0, 0)]
            
        components = []
        power = 0
        current_seed = numeric_seed
        
        while current_seed > 0:
            remainder = current_seed % BASE_DIVISOR
            if remainder > 0:
                components.append((remainder, power))
            
            current_seed //= BASE_DIVISOR
            power += 1
            
        return components
