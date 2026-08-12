from typing import Tuple

"""
Aryabhata Framework Constants

This module stores all the framework constants for the Aryabhata Encoding Engine,
including the Roman Sanskrit symbol mappings (Varga, Avarga, Vowels), positional
values, and validation limits used during the diffusion preprocessing.
"""

# ---------------------------------------------------------
# Roman Sanskrit Symbols (Alphasyllabic Mapping)
# ---------------------------------------------------------

# Varga Consonants map to values 1 through 25 (odd positions)
VARGA_CONSONANTS: Tuple[str, ...] = (
    'k', 'kh', 'g', 'gh', 'ng',  # 1-5
    'c', 'ch', 'j', 'jh', 'ny',  # 6-10
    't', 'th', 'd', 'dh', 'n',   # 11-15 (retroflex)
    't', 'th', 'd', 'dh', 'n',   # 16-20 (dental)
    'p', 'ph', 'b', 'bh', 'm'    # 21-25
)

# Avarga Consonants map to tens starting from 30 (even positions)
# Specifically: 30, 40, 50, 60, 70, 80, 90, 100
AVARGA_CONSONANTS: Tuple[str, ...] = (
    'y', 'r', 'l', 'v', 'sh', 'ss', 's', 'h'
)

# Vowel Multipliers denote powers of 100 (100^0, 100^1, 100^2, ...)
VOWEL_MULTIPLIERS: Tuple[str, ...] = (
    'a', 'i', 'u', 'r', 'l', 'e', 'o', 'ai', 'au'
)


# ---------------------------------------------------------
# Position & Algorithmic Values
# ---------------------------------------------------------

# The Aryabhata system evaluates numbers in Base-100 groups
BASE_DIVISOR: int = 100

# Boundary for Varga calculation
VARGA_MAX_VALUE: int = 25

# Starting multiplier for Avarga logic
AVARGA_START_TENS: int = 30


# ---------------------------------------------------------
# Validation Constants
# ---------------------------------------------------------

# To prevent memory exhaustion during encoding of extremely large seeds
MAX_NUMERIC_SEED_SIZE_BITS: int = 4096

# Minimum required password length before numeric transformation
MIN_PASSWORD_LENGTH: int = 8
