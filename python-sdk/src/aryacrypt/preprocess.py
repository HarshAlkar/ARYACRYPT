from __future__ import annotations

import unicodedata
from typing import Optional, Tuple

from .constants import (
    AVARGA_START_TENS,
    BASE_DIVISOR,
    MAX_NUMERIC_SEED_SIZE_BITS,
    MIN_PASSWORD_LENGTH,
    VARGA_MAX_VALUE,
)
from .errors import AryaCryptError
from .mapping import AryabhataMapping


def transform_password(password: str, mapping: Optional[AryabhataMapping] = None) -> Tuple[str, bytes, int, str]:
    """
    RomanMapper pipeline.

    Returns (nfc_password, stream_bytes, seed, phonetic).
    """
    if not isinstance(password, str):
        raise AryaCryptError(f"Expected password to be a string, got {type(password).__name__}.")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise AryaCryptError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")

    nfc = unicodedata.normalize("NFC", password)
    encoded = nfc.encode("utf-8")
    seed = int.from_bytes(encoded, byteorder="big")
    if seed.bit_length() > MAX_NUMERIC_SEED_SIZE_BITS:
        raise AryaCryptError(
            f"Generated numeric seed exceeds the safety limit of {MAX_NUMERIC_SEED_SIZE_BITS} bits."
        )

    mapper = mapping or AryabhataMapping()
    phonetic = _encode_seed(seed, mapper)
    stream = phonetic.encode("utf-8")
    return nfc, stream, seed, phonetic


def _encode_seed(numeric_seed: int, mapping: AryabhataMapping) -> str:
    encoded_string = ""
    power = 0
    vowel_count = len(mapping.vowel_multipliers)
    seed = numeric_seed

    while seed > 0:
        remainder = seed % BASE_DIVISOR
        seed = seed // BASE_DIVISOR
        vowel = mapping.get_vowel_symbol(power % vowel_count)
        if not vowel:
            raise AryaCryptError(f"Internal Mapping Error: No vowel for power {power % vowel_count}.")

        if 0 < remainder <= VARGA_MAX_VALUE:
            consonant = mapping.get_varga_symbol(remainder)
            if not consonant:
                raise AryaCryptError(f"Internal Mapping Error: Missing Varga for {remainder}.")
            encoded_string = consonant + vowel + encoded_string
        elif remainder > VARGA_MAX_VALUE:
            tens = (remainder // 10) * 10
            units = remainder % 10
            if tens >= AVARGA_START_TENS:
                avarga = mapping.get_avarga_symbol(tens)
                if not avarga:
                    raise AryaCryptError(f"Internal Mapping Error: Missing Avarga for {tens}.")
                encoded_string = avarga + vowel + encoded_string
            if units > 0:
                varga = mapping.get_varga_symbol(units)
                if not varga:
                    raise AryaCryptError(f"Internal Mapping Error: Missing Varga for {units}.")
                encoded_string = varga + vowel + encoded_string
        power += 1

    return encoded_string


def uses_aryabhata(algorithm: str | None) -> bool:
    from .constants import ALGORITHM_ID

    if not algorithm:
        return True
    return "Aryabhata" in algorithm or algorithm == ALGORITHM_ID
