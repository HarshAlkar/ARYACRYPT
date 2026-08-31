from typing import Tuple

VARGA_CONSONANTS: Tuple[str, ...] = (
    "k", "kh", "g", "gh", "ng",
    "c", "ch", "j", "jh", "ny",
    "t", "th", "d", "dh", "n",
    "t", "th", "d", "dh", "n",
    "p", "ph", "b", "bh", "m",
)

AVARGA_CONSONANTS: Tuple[str, ...] = (
    "y", "r", "l", "v", "sh", "ss", "s", "h",
)

VOWEL_MULTIPLIERS: Tuple[str, ...] = (
    "a", "i", "u", "r", "l", "e", "o", "ai", "au",
)

BASE_DIVISOR: int = 100
VARGA_MAX_VALUE: int = 25
AVARGA_START_TENS: int = 30
MAX_NUMERIC_SEED_SIZE_BITS: int = 4096
MIN_PASSWORD_LENGTH: int = 8

SALT_LENGTH_BYTES: int = 16
NONCE_LENGTH_BYTES: int = 12
KEY_LENGTH_BYTES: int = 32
TAG_LENGTH_BYTES: int = 16
PBKDF2_ITERATIONS: int = 600_000
PBKDF2_HASH: str = "sha256"

MAGIC_BYTES: bytes = b"ARYA"
FRAMEWORK_VERSION: str = "1.1.0"
CONTAINER_VERSION: int = 1
ALGORITHM_ID: str = "AryaCrypt-Aryabhata-PBKDF2-AES256GCM"
LEGACY_ALGORITHM_ID: str = "AryaCrypt-PBKDF2-AES256GCM"
MAX_HEADER_LENGTH: int = 10240
CHUNK_SIZE: int = 64 * 1024
