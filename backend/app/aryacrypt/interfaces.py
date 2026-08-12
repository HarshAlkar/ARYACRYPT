"""
Purpose:
Defines the abstract base classes (Interfaces) for the AryaCrypt framework.

Documentation:
To strictly follow SOLID principles (specifically the Dependency Inversion Principle),
the core mathematical modules depend on these interfaces rather than concrete implementations.
This ensures that encoders and mappers can be hot-swapped for testing or future 
PQC (Post-Quantum Cryptography) iterations without rewriting the overarching services.

Unit Test Suggestions:
- Ensure all abstract methods raise NotImplementedError if not overridden.
- Use mock objects inheriting from these interfaces during integration tests.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple

class IRomanMapper(ABC):
    """Interface for mapping numerical chunks to phonetic components."""
    
    @abstractmethod
    def map_varga(self, value: int) -> str:
        """Maps a base-100 Varga value (1-25) to a consonant."""
        pass
        
    @abstractmethod
    def map_avarga(self, value: int) -> str:
        """Maps a base-100 Avarga value (30-100) to a consonant structure."""
        pass
        
    @abstractmethod
    def map_vowel(self, power: int) -> str:
        """Maps an exponential power to a vowel modifier."""
        pass


class IPositionalEncoder(ABC):
    """Interface for breaking down numerical seeds into base-100 positional arrays."""
    
    @abstractmethod
    def extract_positions(self, numeric_seed: int) -> List[Tuple[int, int]]:
        """
        Returns a list of tuples containing (value, power).
        Example: 125 -> [(25, 0), (1, 1)] meaning 25*(100^0) + 1*(100^1).
        """
        pass


class IEncodingEngine(ABC):
    """Interface for orchestrating Mappers and Encoders into a phonetic list."""
    
    @abstractmethod
    def generate_phonetic_fragments(self, numeric_seed: int) -> List[str]:
        """Translates a numeric seed into a sequence of phonetic syllable strings."""
        pass


class IStreamGenerator(ABC):
    """Interface for assembling fragments into the final high-entropy stream."""
    
    @abstractmethod
    def assemble_stream(self, fragments: List[str]) -> str:
        """Concatenates or mathematically weaves phonetic strings into a continuous stream."""
        pass
