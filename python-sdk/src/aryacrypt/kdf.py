import hashlib
import re

from .constants import KEY_LENGTH_BYTES, PBKDF2_HASH, PBKDF2_ITERATIONS, SALT_LENGTH_BYTES
from .errors import AryaCryptError


def derive_key(password_material: bytes, salt: bytes, iterations: int = PBKDF2_ITERATIONS) -> bytes:
    if not isinstance(password_material, bytes):
        raise AryaCryptError("KDF password material must be bytes.")
    if not isinstance(salt, bytes):
        raise AryaCryptError("Salt must be bytes.")
    if len(salt) != SALT_LENGTH_BYTES:
        raise AryaCryptError(f"Salt must be exactly {SALT_LENGTH_BYTES} bytes.")
    if iterations < 100_000:
        raise AryaCryptError("PBKDF2 iterations must be at least 100000.")

    return hashlib.pbkdf2_hmac(
        hash_name=PBKDF2_HASH,
        password=password_material,
        salt=salt,
        iterations=iterations,
        dklen=KEY_LENGTH_BYTES,
    )
