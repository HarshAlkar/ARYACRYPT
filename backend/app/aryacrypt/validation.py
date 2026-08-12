"""
Purpose:
Validates incoming seeds and parameters before they reach the mathematical framework.

Documentation:
The validation layer ensures that the inputs to the Aryabhata Encoding Engine
are mathematically sound. It checks integer boundaries, prevents negative seed inputs,
and guarantees type safety, averting potential crashes deep within the Base-100 logic.

Unit Test Suggestions:
- Test with negative numbers (should raise ValueError).
- Test with extremely large numbers (should pass).
- Test with zero (should raise ValueError or handle gracefully based on spec).
- Test with non-integer inputs (should raise TypeError).
"""

class ValidationLayer:
    @staticmethod
    def validate_seed(seed: int) -> bool:
        """
        Validates that the provided seed is a positive integer suitable for Base-100 mapping.
        
        Args:
            seed (int): The cryptographic seed to validate.
            
        Returns:
            bool: True if valid.
            
        Raises:
            TypeError: If the seed is not an integer.
            ValueError: If the seed is less than or equal to zero.
        """
        if not isinstance(seed, int):
            raise TypeError("Cryptographic seed must be an integer.")
            
        if seed <= 0:
            raise ValueError("Cryptographic seed must be a positive integer strictly greater than zero.")
            
        return True
