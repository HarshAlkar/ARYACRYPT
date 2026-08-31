from __future__ import annotations

from typing import Dict, Optional, Tuple

from .constants import AVARGA_CONSONANTS, VARGA_CONSONANTS, VOWEL_MULTIPLIERS


class AryabhataMapping:
    def __init__(
        self,
        varga_consonants: Tuple[str, ...] = VARGA_CONSONANTS,
        avarga_consonants: Tuple[str, ...] = AVARGA_CONSONANTS,
        vowel_multipliers: Tuple[str, ...] = VOWEL_MULTIPLIERS,
        avarga_start_tens: int = 30,
    ) -> None:
        self.varga_consonants = varga_consonants
        self.avarga_consonants = avarga_consonants
        self.vowel_multipliers = vowel_multipliers
        self.avarga_start_tens = avarga_start_tens
        self._varga_val_to_sym: Dict[int, str] = {}
        self._avarga_val_to_sym: Dict[int, str] = {}
        self._vowel_val_to_sym: Dict[int, str] = {}
        self._build_mappings()

    def _build_mappings(self) -> None:
        for index, symbol in enumerate(self.varga_consonants, start=1):
            self._varga_val_to_sym[index] = symbol
        current_tens = self.avarga_start_tens
        for symbol in self.avarga_consonants:
            self._avarga_val_to_sym[current_tens] = symbol
            current_tens += 10
        for power, symbol in enumerate(self.vowel_multipliers):
            self._vowel_val_to_sym[power] = symbol

    def get_varga_symbol(self, value: int) -> Optional[str]:
        return self._varga_val_to_sym.get(value)

    def get_avarga_symbol(self, value: int) -> Optional[str]:
        return self._avarga_val_to_sym.get(value)

    def get_vowel_symbol(self, power: int) -> Optional[str]:
        return self._vowel_val_to_sym.get(power)
