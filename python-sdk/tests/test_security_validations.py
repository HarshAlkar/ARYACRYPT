"""Format / KDF / password length security tests for Python SDK."""

import pytest
from aryacrypt.errors import AryaCryptError, FormatError
from aryacrypt import format as arya_format
from aryacrypt.kdf import derive_key
from aryacrypt.preprocess import transform_password


def test_non_bmp_password_code_point_length():
    four = "😀" * 4
    assert len(four) == 4
    with pytest.raises(AryaCryptError):
        transform_password(four)
    eight = "😀" * 8
    assert len(eight) == 8
    nfc, stream, seed, phonetic = transform_password(eight)
    assert len(stream) > 0
    assert phonetic


def test_strict_base64_rejected():
    with pytest.raises(FormatError):
        arya_format.decode_b64_field({"salt": "@@@notb64@@"}, "salt")
    with pytest.raises(FormatError):
        arya_format.decode_b64_field({"salt": "abc"}, "salt")  # bad padding length


def test_salt_exact_length():
    with pytest.raises(AryaCryptError):
        derive_key(b"password1", b"short")
