"""
Purpose:
Assembles phonetic fragments into a continuous high-entropy stream.

Documentation:
Once the Aryabhata Encoding Engine generates the list of syllables,
this class concatenates them into a unified string. This string acts
as the final pre-image that will eventually be fed into PBKDF2 (alongside a salt)
to generate the AES key.

Unit Test Suggestions:
- Assemble an empty list (should return "").
- Assemble ["khi", "ghri"] (should return "khighri").
"""

from typing import List
from app.aryacrypt.interfaces import IStreamGenerator

class NumericStreamGenerator(IStreamGenerator):
    
    def assemble_stream(self, fragments: List[str]) -> str:
        """
        Concatenates phonetic fragments into a continuous stream.
        
        Args:
            fragments (List[str]): List of phonetic strings.
            
        Returns:
            str: The unified phonetic stream.
        """
        if not fragments:
            return ""
        return "".join(fragments)
