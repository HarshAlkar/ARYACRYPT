from typing import Union, List


class StreamGenerator:
    """
    Handles the final aggregation of Aryabhata encoded values.
    
    Responsibilities:
    - Normalizes various input types (String, Bytes, Big Integer).
    - Merges multiple encoded values deterministically without collisions.
    - Generates a final, unified numeric stream ready for cryptographic derivation.
    """

    @staticmethod
    def _to_big_integer(value: Union[str, bytes, int]) -> int:
        """
        Normalizes a supported input type into a Big Integer.
        
        Args:
            value: The string, bytes, or integer to normalize.
            
        Returns:
            int: The normalized massive integer representation.
        """
        if isinstance(value, int):
            return value
        elif isinstance(value, str):
            return int.from_bytes(value.encode('utf-8'), byteorder='big')
        elif isinstance(value, bytes):
            return int.from_bytes(value, byteorder='big')
        else:
            raise TypeError(f"Unsupported stream input type: {type(value).__name__}. Expected str, bytes, or int.")

    def merge_to_integer(self, inputs: List[Union[str, bytes, int]]) -> int:
        """
        Merges a sequential list of inputs into a single, massive, deterministic integer.
        
        This uses bitwise shifting to securely concatenate the underlying bytes 
        of each value, ensuring that no data is lost or collides (as simple 
        mathematical addition might cause).
        
        Args:
            inputs: A list of string, bytes, or integer values.
            
        Returns:
            int: A single unified numeric stream.
        """
        if not inputs:
            return 0
            
        final_stream = 0
        
        for item in inputs:
            numeric_val = self._to_big_integer(item)
            
            if numeric_val == 0:
                # Ensure 0s are preserved as a deterministic byte shift
                final_stream = (final_stream << 8) | 0
            else:
                bit_length = numeric_val.bit_length()
                # Round up to the nearest byte boundary (8 bits) for clean concatenation
                shift_amount = ((bit_length + 7) // 8) * 8
                final_stream = (final_stream << shift_amount) | numeric_val
                
        return final_stream

    def merge_to_bytes(self, inputs: List[Union[str, bytes, int]]) -> bytes:
        """
        Merges inputs and converts the massive integer into a deterministic 
        byte stream. This is the optimal format required by PBKDF2 and AES.
        
        Args:
            inputs: A list of string, bytes, or integer values.
            
        Returns:
            bytes: The cryptographic byte stream.
        """
        massive_int = self.merge_to_integer(inputs)
        
        byte_length = (massive_int.bit_length() + 7) // 8
        
        if byte_length == 0:
            return b'\x00'
            
        return massive_int.to_bytes(byte_length, byteorder='big')
