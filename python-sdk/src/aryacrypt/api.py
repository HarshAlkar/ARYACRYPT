from __future__ import annotations

import os
from typing import Optional

from . import aes_gcm, format as arya_format, kdf, preprocess
from .constants import (
    ALGORITHM_ID,
    LEGACY_ALGORITHM_ID,
    MIN_PASSWORD_LENGTH,
    NONCE_LENGTH_BYTES,
    SALT_LENGTH_BYTES,
)
from .errors import AryaCryptError, AuthenticationError, FormatError


class AryaCrypt:
    """Official AryaCrypt Python SDK (spec v1.1.0)."""

    def encrypt(
        self,
        data: bytes,
        password: str,
        *,
        salt: Optional[bytes] = None,
        nonce: Optional[bytes] = None,
        timestamp: Optional[int] = None,
    ) -> bytes:
        if not isinstance(data, bytes):
            raise AryaCryptError("data must be bytes.")
        _, stream, _, _ = preprocess.transform_password(password)
        salt_b = salt if salt is not None else os.urandom(SALT_LENGTH_BYTES)
        nonce_b = nonce if nonce is not None else os.urandom(NONCE_LENGTH_BYTES)
        if len(salt_b) != SALT_LENGTH_BYTES:
            raise AryaCryptError(f"salt must be {SALT_LENGTH_BYTES} bytes.")
        if len(nonce_b) != NONCE_LENGTH_BYTES:
            raise AryaCryptError(f"nonce must be {NONCE_LENGTH_BYTES} bytes.")

        key = kdf.derive_key(stream, salt_b)
        ciphertext, tag = aes_gcm.encrypt_bytes(key, nonce_b, data)
        meta = arya_format.build_metadata(
            salt_b, nonce_b, tag, algorithm=ALGORITHM_ID, timestamp=timestamp
        )
        return arya_format.serialize_header(meta) + ciphertext

    def decrypt(self, encrypted: bytes, password: str) -> bytes:
        if not isinstance(encrypted, bytes):
            raise AryaCryptError("encrypted must be bytes.")
        metadata, ciphertext = arya_format.parse_container(encrypted)
        salt = arya_format.decode_b64_field(metadata, "salt")
        nonce = arya_format.decode_b64_field(metadata, "nonce")
        tag = arya_format.decode_b64_field(metadata, "auth_tag")
        if len(salt) != SALT_LENGTH_BYTES:
            raise FormatError(f"salt must decode to {SALT_LENGTH_BYTES} bytes.")
        if len(nonce) != NONCE_LENGTH_BYTES:
            raise FormatError(f"nonce must decode to {NONCE_LENGTH_BYTES} bytes.")
        algorithm = metadata.get("algorithm", ALGORITHM_ID)

        if preprocess.uses_aryabhata(algorithm):
            _, material, _, _ = preprocess.transform_password(password)
        else:
            material = password.encode("utf-8")

        key = kdf.derive_key(material, salt)
        return aes_gcm.decrypt_bytes(key, nonce, tag, ciphertext)

    def encrypt_legacy(
        self,
        data: bytes,
        password: str,
        *,
        salt: Optional[bytes] = None,
        nonce: Optional[bytes] = None,
        timestamp: Optional[int] = None,
    ) -> bytes:
        """Legacy path: PBKDF2 over raw UTF-8 password (no Aryabhata)."""
        if not isinstance(data, bytes):
            raise AryaCryptError("data must be bytes.")
        if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
            raise AryaCryptError(
                f"Password must be at least {MIN_PASSWORD_LENGTH} characters long."
            )
        salt_b = salt if salt is not None else os.urandom(SALT_LENGTH_BYTES)
        nonce_b = nonce if nonce is not None else os.urandom(NONCE_LENGTH_BYTES)
        if len(salt_b) != SALT_LENGTH_BYTES:
            raise AryaCryptError(f"salt must be {SALT_LENGTH_BYTES} bytes.")
        if len(nonce_b) != NONCE_LENGTH_BYTES:
            raise AryaCryptError(f"nonce must be {NONCE_LENGTH_BYTES} bytes.")
        key = kdf.derive_key(password.encode("utf-8"), salt_b)
        ciphertext, tag = aes_gcm.encrypt_bytes(key, nonce_b, data)
        meta = arya_format.build_metadata(
            salt_b, nonce_b, tag, algorithm=LEGACY_ALGORITHM_ID, timestamp=timestamp
        )
        return arya_format.serialize_header(meta) + ciphertext


__all__ = ["AryaCrypt", "AryaCryptError", "AuthenticationError", "FormatError"]
