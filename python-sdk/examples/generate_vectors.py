"""Generate canonical test vectors into docs/spec/test-vectors/."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aryacrypt import AryaCrypt  # noqa: E402
from aryacrypt import aes_gcm, format as arya_format, kdf, preprocess  # noqa: E402
from aryacrypt.constants import PBKDF2_ITERATIONS  # noqa: E402


def hx(b: bytes) -> str:
    return b.hex()


def build_vector(
    *,
    vid: str,
    password: str,
    plaintext: bytes,
    salt: bytes,
    nonce: bytes,
    timestamp: int = 1_700_000_000,
    legacy: bool = False,
) -> dict:
    crypto = AryaCrypt()
    if legacy:
        material = password.encode("utf-8")
        nfc, stream, seed, phonetic = password, material, None, None
        blob = crypto.encrypt_legacy(
            plaintext, password, salt=salt, nonce=nonce, timestamp=timestamp
        )
    else:
        nfc, stream, seed, phonetic = preprocess.transform_password(password)
        material = stream
        blob = crypto.encrypt(
            plaintext, password, salt=salt, nonce=nonce, timestamp=timestamp
        )

    key = kdf.derive_key(material, salt)
    meta, ct = arya_format.parse_container(blob)
    tag = arya_format.decode_b64_field(meta, "auth_tag")

    return {
        "id": vid,
        "password": password,
        "plaintext_hex": hx(plaintext),
        "nfc_password": nfc,
        "seed_hex": format(seed, "x") if seed is not None else None,
        "phonetic": phonetic,
        "stream_hex": hx(stream) if stream is not None else hx(material),
        "salt_hex": hx(salt),
        "nonce_hex": hx(nonce),
        "iterations": PBKDF2_ITERATIONS,
        "dklen": 32,
        "derived_key_hex": hx(key),
        "ciphertext_hex": hx(ct),
        "tag_hex": hx(tag),
        "timestamp": timestamp,
        "algorithm": meta["algorithm"],
        "arya_blob_hex": hx(blob),
        "legacy": legacy,
    }


def main() -> None:
    out_dir = ROOT / "docs" / "spec" / "test-vectors"
    out_dir.mkdir(parents=True, exist_ok=True)

    salt = bytes.fromhex("00112233445566778899aabbccddeeff")
    nonce = bytes.fromhex("0102030405060708090a0b0c")

    vectors = [
        build_vector(
            vid="basic-ascii",
            password="password1",
            plaintext=b"hello aryacrypt",
            salt=salt,
            nonce=nonce,
        ),
        build_vector(
            vid="binary-payload",
            password="vaultpass1",
            plaintext=bytes(range(256)),
            salt=salt,
            nonce=nonce,
        ),
        build_vector(
            vid="unicode-nfc",
            password="cafe\u0301pass",  # e + combining acute → NFC café…
            plaintext="नमस्ते".encode("utf-8"),
            salt=salt,
            nonce=nonce,
        ),
        build_vector(
            vid="legacy-kdf",
            password="legacyPwd",
            plaintext=b"legacy path",
            salt=salt,
            nonce=nonce,
            legacy=True,
        ),
    ]

    # Preprocess-only edge cases (no full encrypt — documenting RomanMapper)
    edges = []
    for rem_label, synthetic_note in [
        ("compound-37", "remainder 37 compound order"),
    ]:
        # Document phonetic for password that exercises pipeline
        nfc, stream, seed, phonetic = preprocess.transform_password("testpass99")
        edges.append(
            {
                "id": "preprocess-testpass99",
                "note": synthetic_note,
                "password": "testpass99",
                "nfc_password": nfc,
                "seed_hex": format(seed, "x"),
                "phonetic": phonetic,
                "stream_hex": hx(stream),
            }
        )

    # Wrong-password / tamper metadata for negative tests
    good = vectors[0]
    tampered = bytes.fromhex(good["arya_blob_hex"])
    # Flip last ciphertext byte
    arr = bytearray(tampered)
    arr[-1] ^= 0xFF
    negatives = {
        "wrong_password": "password2",
        "short_password": "short",
        "tampered_blob_hex": hx(bytes(arr)),
        "base_vector_id": good["id"],
    }

    (out_dir / "vectors.json").write_text(
        json.dumps({"spec": "1.1.0", "vectors": vectors, "preprocess": edges, "negatives": negatives}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {out_dir / 'vectors.json'} ({len(vectors)} encrypt vectors)")


if __name__ == "__main__":
    main()
