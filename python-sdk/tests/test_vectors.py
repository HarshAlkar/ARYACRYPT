import json
from pathlib import Path

import pytest

from aryacrypt import AryaCrypt, AuthenticationError, FormatError
from aryacrypt import preprocess
from aryacrypt.errors import AryaCryptError

VECTORS_PATH = Path(__file__).resolve().parents[2] / "docs" / "spec" / "test-vectors" / "vectors.json"


@pytest.fixture(scope="module")
def vectors_doc():
    assert VECTORS_PATH.exists(), f"Missing {VECTORS_PATH}; run examples/generate_vectors.py"
    return json.loads(VECTORS_PATH.read_text(encoding="utf-8"))


def test_preprocess_matches_vectors(vectors_doc):
    for item in vectors_doc["preprocess"]:
        nfc, stream, seed, phonetic = preprocess.transform_password(item["password"])
        assert nfc == item["nfc_password"]
        assert phonetic == item["phonetic"]
        assert stream.hex() == item["stream_hex"]
        assert format(seed, "x") == item["seed_hex"]


def test_encrypt_vectors_bit_exact(vectors_doc):
    crypto = AryaCrypt()
    for v in vectors_doc["vectors"]:
        salt = bytes.fromhex(v["salt_hex"])
        nonce = bytes.fromhex(v["nonce_hex"])
        plaintext = bytes.fromhex(v["plaintext_hex"])
        if v.get("legacy"):
            blob = crypto.encrypt_legacy(
                plaintext,
                v["password"],
                salt=salt,
                nonce=nonce,
                timestamp=v["timestamp"],
            )
        else:
            blob = crypto.encrypt(
                plaintext,
                v["password"],
                salt=salt,
                nonce=nonce,
                timestamp=v["timestamp"],
            )
        assert blob.hex() == v["arya_blob_hex"]
        assert crypto.decrypt(blob, v["password"]) == plaintext


def test_wrong_password(vectors_doc):
    crypto = AryaCrypt()
    v = vectors_doc["vectors"][0]
    blob = bytes.fromhex(v["arya_blob_hex"])
    with pytest.raises(AuthenticationError):
        crypto.decrypt(blob, vectors_doc["negatives"]["wrong_password"])


def test_tampered_ciphertext(vectors_doc):
    crypto = AryaCrypt()
    blob = bytes.fromhex(vectors_doc["negatives"]["tampered_blob_hex"])
    with pytest.raises(AuthenticationError):
        crypto.decrypt(blob, vectors_doc["vectors"][0]["password"])


def test_short_password():
    crypto = AryaCrypt()
    with pytest.raises(AryaCryptError):
        crypto.encrypt(b"x", "short")


def test_roundtrip_random():
    crypto = AryaCrypt()
    data = b"random roundtrip " * 1000
    blob = crypto.encrypt(data, "password1")
    assert crypto.decrypt(blob, "password1") == data


def test_bad_magic():
    crypto = AryaCrypt()
    with pytest.raises(FormatError):
        crypto.decrypt(b"NOTA" + b"\x00" * 20, "password1")
