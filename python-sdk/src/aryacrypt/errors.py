class AryaCryptError(Exception):
    """Base error for AryaCrypt SDK."""


class AuthenticationError(AryaCryptError):
    """Wrong password or tampered ciphertext (GCM tag failure)."""


class FormatError(AryaCryptError):
    """Invalid .arya container / metadata."""
