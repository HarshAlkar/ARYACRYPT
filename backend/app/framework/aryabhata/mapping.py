from typing import Dict, Tuple, Optional
from .constants import VARGA_CONSONANTS, AVARGA_CONSONANTS, VOWEL_MULTIPLIERS


class AryabhataMapping:
    """
    Handles the configurable mapping between Roman Characters, Aryabhata Symbols,
    and their corresponding Numeric Values.
    
    This class dynamically builds bidirectional mappings to ensure that the
    business logic is not hardcoded and can be configured or swapped if needed.
    """

    def __init__(
        self,
        varga_consonants: Tuple[str, ...] = VARGA_CONSONANTS,
        avarga_consonants: Tuple[str, ...] = AVARGA_CONSONANTS,
        vowel_multipliers: Tuple[str, ...] = VOWEL_MULTIPLIERS,
        avarga_start_tens: int = 30
    ):
        """
        Initializes the mappings dynamically based on the provided character sets.
        """
        self.varga_consonants = varga_consonants
        self.avarga_consonants = avarga_consonants
        self.vowel_multipliers = vowel_multipliers
        self.avarga_start_tens = avarga_start_tens

        # Mappings: Value -> Symbol
        self._varga_val_to_sym: Dict[int, str] = {}
        self._avarga_val_to_sym: Dict[int, str] = {}
        self._vowel_val_to_sym: Dict[int, str] = {}

        # Mappings: Symbol -> Value
        self._sym_to_varga_val: Dict[str, int] = {}
        self._sym_to_avarga_val: Dict[str, int] = {}
        self._sym_to_vowel_val: Dict[str, int] = {}

        self._build_mappings()

    def _build_mappings(self) -> None:
        """
        Constructs the internal bidirectional dictionaries for O(1) lookups.
        """
        # 1. Varga Mapping (1 to N)
        for index, symbol in enumerate(self.varga_consonants, start=1):
            self._varga_val_to_sym[index] = symbol
            self._sym_to_varga_val[symbol] = index

        # 2. Avarga Mapping (Starting from 30, increments of 10)
        current_tens = self.avarga_start_tens
        for symbol in self.avarga_consonants:
            self._avarga_val_to_sym[current_tens] = symbol
            self._sym_to_avarga_val[symbol] = current_tens
            current_tens += 10

        # 3. Vowel Mapping (Powers of 100)
        for power, symbol in enumerate(self.vowel_multipliers):
            self._vowel_val_to_sym[power] = symbol
            self._sym_to_vowel_val[symbol] = power

    def get_varga_symbol(self, value: int) -> Optional[str]:
        """Retrieves the Varga consonant symbol for a numeric value."""
        return self._varga_val_to_sym.get(value)

    def get_varga_value(self, symbol: str) -> Optional[int]:
        """Retrieves the numeric value for a Varga consonant symbol."""
        return self._sym_to_varga_val.get(symbol)

    def get_avarga_symbol(self, value: int) -> Optional[str]:
        """Retrieves the Avarga consonant symbol for a numeric value."""
        return self._avarga_val_to_sym.get(value)

    def get_avarga_value(self, symbol: str) -> Optional[int]:
        """Retrieves the numeric value for an Avarga consonant symbol."""
        return self._sym_to_avarga_val.get(symbol)

    def get_vowel_symbol(self, power: int) -> Optional[str]:
        """Retrieves the Vowel symbol for a specific power of 100."""
        return self._vowel_val_to_sym.get(power)

    def get_vowel_value(self, symbol: str) -> Optional[int]:
        """Retrieves the power (numeric value) for a given Vowel symbol."""
        return self._sym_to_vowel_val.get(symbol)
