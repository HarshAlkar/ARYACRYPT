"""
Aryabhata Preprocessing Layer for AryaCrypt.

Transforms a user password into a high-entropy byte stream using the
historical Aryabhata Base-100 (katapayadi-style) alphasyllabic system,
then feeds that stream into PBKDF2 for AES-256 key derivation.

Core formula
------------
1. seed = int.from_bytes(UTF-8(NFC(password)), 'big')
2. Decompose seed in Base-100:
       seed = Σ_{i=0}^{n} r_i · 100^i
       where 0 ≤ r_i < 100
3. Map each remainder r_i → Roman-Sanskrit syllable:
       - Varga consonants  (1..25)  → k, kh, g, ... m
       - Avarga consonants (30..100) → y, r, l, v, sh, ss, s, h  (tens)
       - Vowel for power i           → a, i, u, r, l, e, o, ai, au  (100^i)
4. phonetic = concat(syllables)
5. aryacrypt_stream = UTF-8 bytes of phonetic (merged big-int form)
6. AES_key = PBKDF2-HMAC-SHA256(aryacrypt_stream, salt, 600000, 32)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from app.core.logging import logger
from app.framework.aryabhata.constants import (
    BASE_DIVISOR,
    VARGA_MAX_VALUE,
    AVARGA_START_TENS,
    MIN_PASSWORD_LENGTH,
)
from app.framework.aryabhata.roman_mapper import RomanMapper
from app.framework.aryabhata.stream_generator import StreamGenerator
from app.framework.aryabhata.positional import PositionalCalculator


@dataclass(frozen=True)
class AryabhataPreprocessResult:
    """Outputs of the Aryabhata password diffusion layer."""
    phonetic_string: str
    stream_bytes: bytes
    numeric_seed_bits: int
    base100_components: List[Tuple[int, int]]  # (remainder, power)


class AryabhataPreprocessor:
    """
    Shared encrypt/decrypt preprocessing so both paths derive identical keys.
    """

    ALGORITHM_ID = "AryaCrypt-Aryabhata-PBKDF2-AES256GCM"
    LEGACY_ALGORITHM_ID = "AryaCrypt-PBKDF2-AES256GCM"

    def __init__(self) -> None:
        self.mapper = RomanMapper()
        self.stream_gen = StreamGenerator()
        self.positional = PositionalCalculator()

    def transform(self, password: str, *, log: bool = True) -> AryabhataPreprocessResult:
        """
        Run the full Aryabhata diffusion pipeline on a password.

        Raises:
            ValueError / TypeError / OverflowError from RomanMapper on bad input.
        """
        if log:
            self._log_banner()
            logger.info("[A1] Unicode NFC normalize password")
            logger.info(f"     length={len(password)} chars (min={MIN_PASSWORD_LENGTH})")

        # Step A1–A2: normalize + big-integer seed (inside mapper)
        normalized = self.mapper._validate_and_normalize(password)
        numeric_seed = self.mapper._string_to_numeric_seed(normalized)

        if log:
            logger.info("[A2] Convert password -> Aryabhata numeric seed")
            logger.info(
                "     seed = int.from_bytes(UTF-8(password), 'big')"
            )
            logger.info(
                f"     seed_bits={numeric_seed.bit_length()}  "
                f"seed_hex_prefix={hex(numeric_seed)[:18]}..."
            )

        # Step A3: Base-100 decomposition (formula)
        components = self.positional.decompose_number(numeric_seed)

        if log:
            logger.info("[A3] Base-100 (Aryabhata) positional decomposition")
            logger.info(
                f"     Formula: seed = SUM r_i * {BASE_DIVISOR}^i   "
                f"(0 <= r_i < {BASE_DIVISOR})"
            )
            preview = components[:8]
            for rem, power in preview:
                logger.info(
                    f"     r_{power} = {rem:>3}  =>  {rem} * {BASE_DIVISOR}^{power}"
                )
            if len(components) > 8:
                logger.info(f"     ... + {len(components) - 8} more place values")
            logger.info(f"     total_places={len(components)}")

        # Step A4: Roman-Sanskrit mapping
        phonetic = self.mapper.encode(password)

        if log:
            logger.info("[A4] Map remainders -> Varga/Avarga consonants + vowel powers")
            logger.info(
                f"     Varga  (1..{VARGA_MAX_VALUE}): consonant syllables"
            )
            logger.info(
                f"     Avarga (>={AVARGA_START_TENS}): tens consonants y,r,l,v,sh,ss,s,h"
            )
            logger.info(
                f"     Vowels: power-of-{BASE_DIVISOR} markers (a,i,u,...)"
            )
            preview_phonetic = phonetic if len(phonetic) <= 64 else phonetic[:64] + "..."
            logger.info(f"     phonetic = '{preview_phonetic}'")
            logger.info(f"     phonetic_len = {len(phonetic)} chars")

        # Step A5: Aggregate to cryptographic byte stream
        stream_bytes = self.stream_gen.merge_to_bytes([phonetic])

        if log:
            logger.info("[A5] Aggregate phonetic string -> AryaCrypt byte stream")
            logger.info(
                f"     stream_len={len(stream_bytes)} bytes  "
                f"prefix={stream_bytes[:12].hex()}..."
            )
            logger.info("[A6] Hand stream to PBKDF2-HMAC-SHA256 (next crypto step)")
            logger.info("-" * 64)

        return AryabhataPreprocessResult(
            phonetic_string=phonetic,
            stream_bytes=stream_bytes,
            numeric_seed_bits=numeric_seed.bit_length(),
            base100_components=components,
        )

    @staticmethod
    def uses_aryabhata(algorithm: str | None) -> bool:
        """True when file metadata indicates Aryabhata-preprocessed keys."""
        if not algorithm:
            # New default when field missing on brand-new writes
            return True
        return "Aryabhata" in algorithm or algorithm == AryabhataPreprocessor.ALGORITHM_ID

    @staticmethod
    def _log_banner() -> None:
        logger.info("-" * 64)
        logger.info("ARYABHATA PREPROCESSING LAYER")
        logger.info("Formula: seed = SUM r_i * 100^i -> Roman-Sanskrit -> PBKDF2 stream")
        logger.info("-" * 64)
