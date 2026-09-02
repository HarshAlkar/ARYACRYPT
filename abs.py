"""Step-by-step AryaCrypt encrypt / decrypt walkthrough (prints each stage)."""

import os
from pathlib import Path

from aryacrypt import AryaCrypt
from aryacrypt import format as arya_format
from aryacrypt.aes_gcm import decrypt_bytes, encrypt_bytes
from aryacrypt.constants import (
    ALGORITHM_ID,
    FRAMEWORK_VERSION,
    MAGIC_BYTES,
    PBKDF2_ITERATIONS,
)
from aryacrypt.kdf import derive_key
from aryacrypt.preprocess import transform_password


def banner(title: str) -> None:
    print()
    print("=" * 72)
    print(f"  {title}")
    print("=" * 72)


def step(n: str, title: str) -> None:
    print()
    print(f"[{n}] {title}")
    print("-" * 72)


def preview(label: str, data: bytes, limit: int = 48) -> None:
    shown = data[:limit].hex()
    extra = f"  ... (+{len(data) - limit} more bytes)" if len(data) > limit else ""
    print(f"    {label}: {shown}{extra}")
    print(f"    length : {len(data)} bytes")


PLAINTEXT = b"hello Teammmm"
PASSWORD = "password1"
OUT_FILE = Path("secret.arya")


def main() -> None:
    banner("ARYACRYPT  --  ENCRYPTION")
    print(f"    plaintext : {PLAINTEXT!r}")
    print(f"    password  : {PASSWORD!r}")

    step("1", "Unicode NFC normalize the password")
    nfc, stream, seed, phonetic = transform_password(PASSWORD)
    print(f"    NFC password : {nfc!r}")
    print("    (same as typed if already NFC)")

    step("2", "Turn password bytes into a numeric seed")
    print(f"    UTF-8 bytes  : {nfc.encode('utf-8').hex()}")
    print(f"    seed (hex)   : {format(seed, 'x')}")
    print(f"    seed bits    : {seed.bit_length()}")

    step("3", "Aryabhata / RomanMapper encode that seed")
    print(f"    phonetic stream (text) : {phonetic}")
    preview("phonetic UTF-8", stream)
    print("    this stream -- not the raw password -- goes into PBKDF2")

    step("4", "Generate random salt (16 bytes) and nonce (12 bytes)")
    crypto = AryaCrypt()
    salt = os.urandom(16)
    nonce = os.urandom(12)
    preview("salt ", salt)
    preview("nonce", nonce)

    step("5", f"PBKDF2-HMAC-SHA256  ->  32-byte AES key  ({PBKDF2_ITERATIONS:,} iterations)")
    print("    input : Aryabhata stream + salt")
    key = derive_key(stream, salt)
    preview("AES-256 key", key)
    print("    (key is never stored in the .arya file)")

    step("6", "AES-256-GCM encrypt the plaintext")
    ciphertext, tag = encrypt_bytes(key, nonce, PLAINTEXT)
    preview("ciphertext", ciphertext)
    preview("auth tag  ", tag)
    print("    GCM tag proves the file was not tampered with")

    step("7", "Pack a .arya container  (ARYA + header length + JSON + ciphertext)")
    meta = arya_format.build_metadata(salt, nonce, tag, algorithm=ALGORITHM_ID)
    header = arya_format.serialize_header(meta)
    blob = header + ciphertext
    print(f"    magic          : {MAGIC_BYTES!r}")
    print(f"    framework      : {FRAMEWORK_VERSION}")
    print(f"    algorithm      : {ALGORITHM_ID}")
    print(f"    header JSON    : {meta}")
    print(f"    header bytes   : {len(header)}  (4 magic + 4 length + JSON)")
    print(f"    ciphertext     : {len(ciphertext)} bytes")
    print(f"    total blob     : {len(blob)} bytes")
    OUT_FILE.write_bytes(blob)
    print(f"    wrote          : {OUT_FILE.resolve()}")

    banner("ARYACRYPT  --  DECRYPTION")
    print(f"    reading : {OUT_FILE}")

    step("8", "Parse the .arya file")
    stored = OUT_FILE.read_bytes()
    print(f"    magic bytes    : {stored[:4]!r}")
    metadata, ct = arya_format.parse_container(stored)
    salt_d = arya_format.decode_b64_field(metadata, "salt")
    nonce_d = arya_format.decode_b64_field(metadata, "nonce")
    tag_d = arya_format.decode_b64_field(metadata, "auth_tag")
    print(f"    algorithm      : {metadata.get('algorithm')}")
    preview("salt from header", salt_d)
    preview("nonce from header", nonce_d)
    preview("tag from header ", tag_d)
    preview("ciphertext      ", ct)

    step("9", "Rebuild the same key from the password (same preprocess + PBKDF2)")
    _, stream_d, _, phonetic_d = transform_password(PASSWORD)
    print(f"    phonetic stream : {phonetic_d}")
    key_d = derive_key(stream_d, salt_d)
    preview("derived AES key", key_d)
    print(f"    matches encrypt key : {key_d == key}")

    step("10", "AES-256-GCM decrypt + verify auth tag")
    recovered = decrypt_bytes(key_d, nonce_d, tag_d, ct)
    print(f"    recovered plaintext : {recovered!r}")
    print(f"    matches original    : {recovered == PLAINTEXT}")

    step("11", "Same result via the public SDK (one-liner)")
    via_sdk = crypto.decrypt(stored, PASSWORD)
    print(f"    AryaCrypt.decrypt() : {via_sdk!r}")

    banner("DONE")
    print("    password -> NFC -> Aryabhata stream -> PBKDF2 -> AES-256-GCM -> .arya")
    print("    decrypt reverses that using salt/nonce/tag stored in the header")
    print()


if __name__ == "__main__":
    main()
