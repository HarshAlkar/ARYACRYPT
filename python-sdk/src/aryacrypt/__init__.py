"""AryaCrypt — password preprocessing + PBKDF2-HMAC-SHA256 + AES-256-GCM."""

from .api import AryaCrypt
from .constants import (
    ALGORITHM_ID,
    FRAMEWORK_VERSION,
    LEGACY_ALGORITHM_ID,
    MIN_PASSWORD_LENGTH,
)
from .errors import AryaCryptError, AuthenticationError, FormatError

__all__ = [
    "AryaCrypt",
    "AryaCryptError",
    "AuthenticationError",
    "FormatError",
    "ALGORITHM_ID",
    "FRAMEWORK_VERSION",
    "LEGACY_ALGORITHM_ID",
    "MIN_PASSWORD_LENGTH",
]

__version__ = "1.1.0"
