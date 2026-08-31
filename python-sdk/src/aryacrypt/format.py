from __future__ import annotations

import base64
import json
import re
import struct
from datetime import datetime, timezone
from typing import Any, Dict, Tuple

from .constants import (
    ALGORITHM_ID,
    CONTAINER_VERSION,
    FRAMEWORK_VERSION,
    MAGIC_BYTES,
    MAX_HEADER_LENGTH,
)
from .errors import FormatError


def build_metadata(
    salt: bytes,
    nonce: bytes,
    auth_tag: bytes,
    *,
    algorithm: str = ALGORITHM_ID,
    timestamp: int | None = None,
    version: int = CONTAINER_VERSION,
) -> Dict[str, Any]:
    return {
        "version": version,
        "framework_version": FRAMEWORK_VERSION,
        "algorithm": algorithm,
        "salt": base64.b64encode(salt).decode("utf-8"),
        "nonce": base64.b64encode(nonce).decode("utf-8"),
        "auth_tag": base64.b64encode(auth_tag).decode("utf-8"),
        "timestamp": int(datetime.now(timezone.utc).timestamp()) if timestamp is None else timestamp,
    }


def serialize_header(metadata: Dict[str, Any]) -> bytes:
    try:
        json_bytes = json.dumps(metadata, separators=(",", ":")).encode("utf-8")
    except Exception as exc:
        raise FormatError(f"Failed to encode metadata JSON: {exc}") from exc
    return MAGIC_BYTES + struct.pack(">I", len(json_bytes)) + json_bytes


def parse_container(blob: bytes) -> Tuple[Dict[str, Any], bytes]:
    if len(blob) < 8:
        raise FormatError("Truncated .arya container.")
    if blob[:4] != MAGIC_BYTES:
        raise FormatError("Invalid file format. Magic bytes 'ARYA' not found.")
    header_length = struct.unpack(">I", blob[4:8])[0]
    if header_length > MAX_HEADER_LENGTH:
        raise FormatError(f"Unsafely massive header detected ({header_length} bytes).")
    end = 8 + header_length
    if len(blob) < end:
        raise FormatError("Unexpected end of file while reading JSON header.")
    try:
        metadata = json.loads(blob[8:end].decode("utf-8"))
    except json.JSONDecodeError:
        raise FormatError("Invalid metadata JSON.")
    return metadata, blob[end:]


def deserialize_from_stream(in_stream) -> Tuple[Dict[str, Any], int]:
    """Parse ARYA header from a binary stream; leaves stream at ciphertext start."""
    magic = in_stream.read(4)
    if magic != MAGIC_BYTES:
        raise FormatError("Invalid file format. Magic bytes 'ARYA' not found.")
    length_bytes = in_stream.read(4)
    if len(length_bytes) < 4:
        raise FormatError("Corrupted file header. Missing 4-byte length indicator.")
    header_length = struct.unpack(">I", length_bytes)[0]
    if header_length > MAX_HEADER_LENGTH:
        raise FormatError(f"Unsafely massive header detected ({header_length} bytes).")
    json_bytes = in_stream.read(header_length)
    if len(json_bytes) < header_length:
        raise FormatError("Unexpected end of file while reading JSON header.")
    try:
        metadata = json.loads(json_bytes.decode("utf-8"))
    except json.JSONDecodeError:
        raise FormatError("Invalid metadata JSON.")
    return metadata, 4 + 4 + header_length


def decode_b64_field(metadata: Dict[str, Any], key: str) -> bytes:
    raw = metadata.get(key)
    if not isinstance(raw, str) or not raw:
        raise FormatError(f"Invalid or missing metadata field '{key}'.")
    # Strict standard Base64 (reject URL-safe / whitespace / missing padding)
    if not re.fullmatch(r"[A-Za-z0-9+/]+={0,2}", raw):
        raise FormatError(f"Invalid Base64 in metadata field '{key}'.")
    if len(raw) % 4 != 0:
        raise FormatError(f"Invalid Base64 padding in metadata field '{key}'.")
    try:
        return base64.b64decode(raw, validate=True)
    except Exception as exc:
        raise FormatError(f"Invalid or missing metadata field '{key}'.") from exc
