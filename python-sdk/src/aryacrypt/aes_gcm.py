from __future__ import annotations

import io
import os
import tempfile
from pathlib import Path
from typing import BinaryIO

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from .constants import CHUNK_SIZE, KEY_LENGTH_BYTES, NONCE_LENGTH_BYTES, TAG_LENGTH_BYTES
from .errors import AryaCryptError, AuthenticationError


def encrypt_bytes(key: bytes, nonce: bytes, plaintext: bytes) -> tuple[bytes, bytes]:
    _validate_key_nonce(key, nonce)
    encryptor = Cipher(algorithms.AES(key), modes.GCM(nonce)).encryptor()
    out = io.BytesIO()
    view = memoryview(plaintext)
    for i in range(0, len(plaintext), CHUNK_SIZE):
        out.write(encryptor.update(view[i : i + CHUNK_SIZE]))
    encryptor.finalize()
    return out.getvalue(), encryptor.tag


def decrypt_bytes(key: bytes, nonce: bytes, tag: bytes, ciphertext: bytes) -> bytes:
    _validate_key_nonce(key, nonce)
    if len(tag) != TAG_LENGTH_BYTES:
        raise AryaCryptError(f"Auth tag must be {TAG_LENGTH_BYTES} bytes.")
    try:
        decryptor = Cipher(algorithms.AES(key), modes.GCM(nonce, tag)).decryptor()
        out = io.BytesIO()
        view = memoryview(ciphertext)
        for i in range(0, len(ciphertext), CHUNK_SIZE):
            out.write(decryptor.update(view[i : i + CHUNK_SIZE]))
        decryptor.finalize()
        return out.getvalue()
    except InvalidTag as exc:
        raise AuthenticationError(
            "Authentication failed: incorrect password or tampered ciphertext."
        ) from exc


def encrypt_stream(key: bytes, nonce: bytes, in_stream: BinaryIO, out_stream: BinaryIO) -> bytes:
    _validate_key_nonce(key, nonce)
    encryptor = Cipher(algorithms.AES(key), modes.GCM(nonce)).encryptor()
    while True:
        chunk = in_stream.read(CHUNK_SIZE)
        if not chunk:
            break
        out_stream.write(encryptor.update(chunk))
    encryptor.finalize()
    return encryptor.tag


def decrypt_stream(
    key: bytes, nonce: bytes, tag: bytes, in_stream: BinaryIO, out_stream: BinaryIO
) -> None:
    """
    Decrypt a ciphertext stream.

    Plaintext is written to a private temporary file and only copied to
    ``out_stream`` after AES-GCM authentication succeeds (finalize).
    On auth failure the temp file is deleted and AuthenticationError is raised.
    """
    _validate_key_nonce(key, nonce)
    if len(tag) != TAG_LENGTH_BYTES:
        raise AryaCryptError(f"Auth tag must be {TAG_LENGTH_BYTES} bytes.")

    fd, tmp_name = tempfile.mkstemp(prefix="aryacrypt_dec_", suffix=".tmp")
    os.close(fd)
    tmp_path = Path(tmp_name)
    try:
        decryptor = Cipher(algorithms.AES(key), modes.GCM(nonce, tag)).decryptor()
        with open(tmp_path, "wb") as tmp_out:
            while True:
                chunk = in_stream.read(CHUNK_SIZE)
                if not chunk:
                    break
                tmp_out.write(decryptor.update(chunk))
            decryptor.finalize()

        # Auth OK — promote plaintext
        with open(tmp_path, "rb") as tmp_in:
            while True:
                chunk = tmp_in.read(CHUNK_SIZE)
                if not chunk:
                    break
                out_stream.write(chunk)
    except InvalidTag as exc:
        raise AuthenticationError(
            "Authentication failed: incorrect password or tampered ciphertext."
        ) from exc
    finally:
        try:
            if tmp_path.exists():
                tmp_path.unlink()
        except OSError:
            pass


def _validate_key_nonce(key: bytes, nonce: bytes) -> None:
    if len(key) != KEY_LENGTH_BYTES:
        raise AryaCryptError(f"AES key must be {KEY_LENGTH_BYTES} bytes.")
    if len(nonce) != NONCE_LENGTH_BYTES:
        raise AryaCryptError(f"Nonce must be {NONCE_LENGTH_BYTES} bytes.")
